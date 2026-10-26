"""Arduino Starter — PlatformIO Upload & Monitor desktop UI."""
from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from pio_runner import find_pio, parse_platformio_ini, run_upload
from serial_monitor import SerialMonitor, list_ports, wait_for_app_port

APP_TITLE = "Arduino Starter — Upload & Monitor"
SETTINGS_PATH = Path.home() / ".arduino_starter.json"
DEFAULT_PROJECT = (
    Path(__file__).resolve().parent.parent / "HardwareTest"
)


class ArduinoStarterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("960x640")
        self.minsize(720, 480)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._pio = find_pio()
        self._envs: dict[str, int] = {}  # name -> baud
        self._port_map: dict[str, str] = {}  # label -> device
        self._busy = False
        self._monitor = SerialMonitor(
            on_line=self._log_threadsafe,
            on_stopped=self._on_monitor_stopped,
        )

        self._build_ui()
        self._load_settings()
        self.refresh_ports()
        self._update_pio_status()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # --- UI ---

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        top = ctk.CTkFrame(self)
        top.pack(fill="x", **pad)

        # Project
        ctk.CTkLabel(top, text="Projekt").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.project_var = tk.StringVar()
        self.project_entry = ctk.CTkEntry(top, textvariable=self.project_var, width=520)
        self.project_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=6, pady=4)
        ctk.CTkButton(top, text="Browse…", width=100, command=self.browse_project).grid(
            row=0, column=3, padx=6, pady=4
        )

        # Env + baud
        ctk.CTkLabel(top, text="Environment").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.env_var = tk.StringVar()
        self.env_menu = ctk.CTkOptionMenu(
            top, variable=self.env_var, values=["—"], command=self._on_env_change, width=220
        )
        self.env_menu.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkLabel(top, text="Baud").grid(row=1, column=2, sticky="e", padx=6, pady=4)
        self.baud_var = tk.StringVar(value="9600")
        self.baud_entry = ctk.CTkEntry(top, textvariable=self.baud_var, width=100)
        self.baud_entry.grid(row=1, column=3, sticky="w", padx=6, pady=4)

        # Port
        ctk.CTkLabel(top, text="COM-port").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.port_var = tk.StringVar()
        self.port_menu = ctk.CTkOptionMenu(top, variable=self.port_var, values=["—"], width=420)
        self.port_menu.grid(row=2, column=1, columnspan=2, sticky="ew", padx=6, pady=4)
        ctk.CTkButton(top, text="Refresh", width=100, command=self.refresh_ports).grid(
            row=2, column=3, padx=6, pady=4
        )

        top.grid_columnconfigure(1, weight=1)

        # Buttons
        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", **pad)
        self.btn_upload = ctk.CTkButton(btns, text="Upload", command=self.do_upload, width=120)
        self.btn_upload.pack(side="left", padx=6, pady=8)
        self.btn_monitor = ctk.CTkButton(btns, text="Monitor", command=self.do_monitor, width=120)
        self.btn_monitor.pack(side="left", padx=6, pady=8)
        self.btn_both = ctk.CTkButton(
            btns, text="Upload & Monitor", command=self.do_upload_and_monitor, width=160,
            fg_color="#1f6aa5", hover_color="#144870",
        )
        self.btn_both.pack(side="left", padx=6, pady=8)
        self.btn_stop = ctk.CTkButton(
            btns, text="Stop monitor", command=self.do_stop_monitor, width=120,
            fg_color="#8B3A3A", hover_color="#6B2A2A",
        )
        self.btn_stop.pack(side="left", padx=6, pady=8)
        ctk.CTkButton(btns, text="Clear", command=self.clear_log, width=80).pack(
            side="right", padx=6, pady=8
        )

        # Log
        self.log = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13))
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Status
        self.status_var = tk.StringVar(value="Klar")
        self.status = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w")
        self.status.pack(fill="x", padx=12, pady=(0, 8))

        self.project_var.trace_add("write", lambda *_: self.after(400, self._reload_envs_debounced))
        self._env_reload_token = 0

    # --- settings ---

    def _load_settings(self) -> None:
        project = DEFAULT_PROJECT if DEFAULT_PROJECT.is_dir() else None
        if SETTINGS_PATH.is_file():
            try:
                data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
                p = data.get("project")
                if p and Path(p).is_dir():
                    project = Path(p)
            except (json.JSONDecodeError, OSError):
                pass
        if project:
            self.project_var.set(str(project))
            self._reload_envs()

    def _save_settings(self) -> None:
        try:
            SETTINGS_PATH.write_text(
                json.dumps({"project": self.project_var.get()}, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    # --- helpers ---

    def _update_pio_status(self) -> None:
        if self._pio:
            self._log(f"PlatformIO: {self._pio}")
        else:
            self._log("ADVARSEL: platformio/pio ikke fundet i PATH.")
            self.set_status("Fejl: PlatformIO mangler")

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _log(self, line: str) -> None:
        self.log.insert("end", line + "\n")
        self.log.see("end")

    def _log_threadsafe(self, line: str) -> None:
        self.after(0, lambda: self._log(line))

    def clear_log(self) -> None:
        self.log.delete("1.0", "end")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        for btn in (self.btn_upload, self.btn_monitor, self.btn_both):
            btn.configure(state=state)

    def _selected_port_device(self) -> str | None:
        label = self.port_var.get()
        if not label or label == "—":
            return None
        return self._port_map.get(label, label.split(" — ")[0].strip())

    def _selected_baud(self) -> int:
        try:
            return int(self.baud_var.get().strip())
        except ValueError:
            return 9600

    # --- project / env / ports ---

    def browse_project(self) -> None:
        path = filedialog.askdirectory(
            title="Vælg PlatformIO-projekt",
            initialdir=self.project_var.get() or str(Path.home()),
        )
        if path:
            self.project_var.set(path)
            self._reload_envs()
            self._save_settings()

    def _reload_envs_debounced(self) -> None:
        self._env_reload_token += 1
        token = self._env_reload_token
        self.after(350, lambda: self._reload_envs() if token == self._env_reload_token else None)

    def _reload_envs(self) -> None:
        project = self.project_var.get().strip()
        if not project or not (Path(project) / "platformio.ini").is_file():
            self.env_menu.configure(values=["—"])
            self.env_var.set("—")
            self._envs.clear()
            return
        try:
            envs = parse_platformio_ini(project)
        except Exception as e:
            self._log(f"Kunne ikke læse platformio.ini: {e}")
            return
        if not envs:
            self.env_menu.configure(values=["—"])
            self.env_var.set("—")
            self._envs.clear()
            return
        names = [e.name for e in envs]
        self._envs = {e.name: e.monitor_speed for e in envs}
        self.env_menu.configure(values=names)
        current = self.env_var.get()
        if current not in names:
            self.env_var.set(names[0])
        self._on_env_change(self.env_var.get())

    def _on_env_change(self, name: str) -> None:
        if name in self._envs:
            self.baud_var.set(str(self._envs[name]))

    def refresh_ports(self) -> None:
        ports = list_ports()
        if not ports:
            self._port_map = {}
            self.port_menu.configure(values=["Ingen porte"])
            self.port_var.set("Ingen porte")
            return
        labels = []
        self._port_map = {}
        prev = self._selected_port_device()
        for p in ports:
            labels.append(p.label)
            self._port_map[p.label] = p.device
        self.port_menu.configure(values=labels)
        # Behold tidligere valg hvis muligt
        chosen = None
        if prev:
            for lab, dev in self._port_map.items():
                if dev.upper() == prev.upper():
                    chosen = lab
                    break
        if not chosen:
            # Foretræk ikke-bootloader
            for p in ports:
                if not p.is_bootloader:
                    chosen = p.label
                    break
            if not chosen:
                chosen = labels[0]
        self.port_var.set(chosen)
        for p in ports:
            if p.is_bootloader:
                self._log(f"Tip: {p.device} er i bootloader-mode")

    # --- actions ---

    def do_upload(self) -> None:
        self._start_job(upload=True, monitor=False)

    def do_monitor(self) -> None:
        if self._busy:
            return
        port = self._selected_port_device()
        if not port:
            messagebox.showwarning(APP_TITLE, "Vælg en COM-port.")
            return
        try:
            self._monitor.start(port, self._selected_baud())
            self.set_status(f"Monitoring {port}")
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))

    def do_upload_and_monitor(self) -> None:
        self._start_job(upload=True, monitor=True)

    def do_stop_monitor(self) -> None:
        self._monitor.stop()
        self.set_status("Monitor stoppet")

    def _on_monitor_stopped(self) -> None:
        self.after(0, lambda: self.set_status("Klar") if not self._busy else None)

    def _start_job(self, upload: bool, monitor: bool) -> None:
        if self._busy:
            return
        project = self.project_var.get().strip()
        env = self.env_var.get().strip()
        port = self._selected_port_device()

        if not project or not (Path(project) / "platformio.ini").is_file():
            messagebox.showwarning(APP_TITLE, "Vælg en mappe med platformio.ini.")
            return
        if not env or env == "—":
            messagebox.showwarning(APP_TITLE, "Vælg et environment.")
            return
        if not port:
            messagebox.showwarning(APP_TITLE, "Vælg en COM-port.")
            return
        if not self._pio:
            self._pio = find_pio()
        if not self._pio:
            messagebox.showerror(APP_TITLE, "PlatformIO CLI ikke fundet.")
            return

        self._save_settings()
        self._set_busy(True)
        baud = self._selected_baud()

        def worker() -> None:
            try:
                # Frigør port før upload
                if self._monitor.is_running:
                    self._log_threadsafe("Stopper monitor før upload…")
                    self._monitor.stop()
                    import time
                    time.sleep(0.5)

                if upload:
                    self.after(0, lambda: self.set_status("Uploader…"))
                    code = run_upload(
                        project_dir=project,
                        env_name=env,
                        port=port,
                        on_line=self._log_threadsafe,
                        pio_path=self._pio,
                    )
                    if code != 0:
                        self._log_threadsafe(f"Upload fejlede (exit {code})")
                        self.after(0, lambda: self.set_status(f"Fejl (exit {code})"))
                        return

                    self._log_threadsafe("Upload OK")
                    self.after(0, self.refresh_ports)

                if monitor:
                    self.after(0, lambda: self.set_status("Venter på board…"))
                    app_port = wait_for_app_port(preferred=port, timeout=25.0)
                    if not app_port:
                        self._log_threadsafe("FEJL: ingen COM-port efter upload")
                        self.after(0, lambda: self.set_status("Fejl: ingen port"))
                        return
                    self._log_threadsafe(f"Åbner monitor på {app_port}")

                    def start_mon() -> None:
                        self.refresh_ports()
                        # Opdater dropdown til app_port
                        for lab, dev in self._port_map.items():
                            if dev.upper() == app_port.upper():
                                self.port_var.set(lab)
                                break
                        try:
                            self._monitor.start(app_port, baud)
                            self.set_status(f"Monitoring {app_port}")
                        except Exception as e:
                            self._log(f"Monitor-fejl: {e}")
                            self.set_status("Fejl: monitor")

                    self.after(0, start_mon)
                else:
                    self.after(0, lambda: self.set_status("Upload færdig"))
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def _on_close(self) -> None:
        self._monitor.stop()
        self._save_settings()
        self.destroy()


def main() -> None:
    app = ArduinoStarterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
