"""Arduino Starter — PlatformIO Upload & Monitor desktop UI."""
from __future__ import annotations

import json
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from log_style import TAG_COLORS, classify_line
from pio_runner import find_pio, parse_platformio_ini, run_pio, run_powershell, run_upload
from secrets_editor import (
    ensure_secrets_file,
    find_secrets_path,
    open_secrets_dialog,
    secrets_looks_valid,
)
from serial_monitor import (
    SerialMonitor,
    list_ports,
    pick_best_port,
    wait_for_app_port,
)

APP_TITLE = "Arduino Starter — Upload & Monitor"
SETTINGS_PATH = Path.home() / ".arduino_starter.json"
STARTER_DIR = Path(__file__).resolve().parent
HARDWARETESTERE = STARTER_DIR.parent
REPO_ROOT = HARDWARETESTERE.parent
DEFAULT_PROJECT = HARDWARETESTERE / "HardwareTest"
UPDATE_DEVICE_PS1 = HARDWARETESTERE / "Update-Device.ps1"

FONT_SIZES = (13, 16, 20, 24)


def _default_favorites() -> list[dict[str, str]]:
    """Scan repo for PlatformIO-projekter + kendte mapper."""
    found: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(name: str, path: Path) -> None:
        key = str(path.resolve()).lower()
        if key in seen or not path.is_dir():
            return
        if not (path / "platformio.ini").is_file():
            return
        seen.add(key)
        found.append({"name": name, "path": str(path.resolve())})

    add("HardwareTest", DEFAULT_PROJECT)
    for base in (HARDWARETESTERE, REPO_ROOT):
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                add(child.name, child)
    return found


class ArduinoStarterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x680")
        self.minsize(780, 520)

        self._theme = "dark"
        self._font_size = 16
        self._favorites: list[dict[str, str]] = _default_favorites()
        self._load_settings_data()

        ctk.set_appearance_mode(self._theme)
        ctk.set_default_color_theme("blue")

        self._pio = find_pio()
        self._envs: dict[str, int] = {}
        self._port_map: dict[str, str] = {}
        self._busy = False
        self._action_buttons: list[ctk.CTkButton] = []
        self._fav_buttons: list[ctk.CTkButton] = []
        self._monitor = SerialMonitor(
            on_line=self._log_threadsafe,
            on_stopped=self._on_monitor_stopped,
        )

        self._build_ui()
        self._apply_project_from_settings()
        self._rebuild_favorite_buttons()
        self._apply_log_tags()
        self._apply_font()
        self.refresh_ports(auto_select=True)
        self._update_pio_status()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        top = ctk.CTkFrame(self)
        top.pack(fill="x", **pad)

        ctk.CTkLabel(top, text="Projekt").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.project_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=self.project_var, width=520).grid(
            row=0, column=1, columnspan=2, sticky="ew", padx=6, pady=4
        )
        ctk.CTkButton(top, text="Browse…", width=100, command=self.browse_project).grid(
            row=0, column=3, padx=6, pady=4
        )

        # Favoritter
        ctk.CTkLabel(top, text="Favoritter").grid(row=1, column=0, sticky="nw", padx=6, pady=4)
        self.fav_frame = ctk.CTkFrame(top, fg_color="transparent")
        self.fav_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=6, pady=4)
        fav_actions = ctk.CTkFrame(top, fg_color="transparent")
        fav_actions.grid(row=1, column=3, sticky="e", padx=6, pady=4)
        ctk.CTkButton(fav_actions, text="+ Favorit", width=90, command=self.add_favorite).pack(
            side="top", pady=2
        )
        ctk.CTkButton(fav_actions, text="− Favorit", width=90, command=self.remove_favorite).pack(
            side="top", pady=2
        )

        ctk.CTkLabel(top, text="Environment").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.env_var = tk.StringVar()
        self.env_menu = ctk.CTkOptionMenu(
            top, variable=self.env_var, values=["—"], command=self._on_env_change, width=220
        )
        self.env_menu.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkLabel(top, text="Baud").grid(row=2, column=2, sticky="e", padx=6, pady=4)
        self.baud_var = tk.StringVar(value="9600")
        ctk.CTkEntry(top, textvariable=self.baud_var, width=100).grid(
            row=2, column=3, sticky="w", padx=6, pady=4
        )

        ctk.CTkLabel(top, text="COM-port").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.port_var = tk.StringVar()
        self.port_menu = ctk.CTkOptionMenu(top, variable=self.port_var, values=["—"], width=360)
        self.port_menu.grid(row=3, column=1, sticky="ew", padx=6, pady=4)

        port_btns = ctk.CTkFrame(top, fg_color="transparent")
        port_btns.grid(row=3, column=2, columnspan=2, sticky="e", padx=6, pady=4)
        ctk.CTkButton(port_btns, text="Auto", width=70, command=self.auto_select_port).pack(
            side="left", padx=3
        )
        ctk.CTkButton(port_btns, text="Refresh", width=80, command=lambda: self.refresh_ports()).pack(
            side="left", padx=3
        )

        top.grid_columnconfigure(1, weight=1)

        # Primary actions
        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", **pad)
        self.btn_upload = ctk.CTkButton(btns, text="Upload", command=self.do_upload, width=100)
        self.btn_monitor = ctk.CTkButton(btns, text="Monitor", command=self.do_monitor, width=100)
        self.btn_both = ctk.CTkButton(
            btns,
            text="Upload & Monitor",
            command=self.do_upload_and_monitor,
            width=150,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        self.btn_stop = ctk.CTkButton(
            btns,
            text="Stop monitor",
            command=self.do_stop_monitor,
            width=110,
            fg_color="#8B3A3A",
            hover_color="#6B2A2A",
        )
        for b in (self.btn_upload, self.btn_monitor, self.btn_both, self.btn_stop):
            b.pack(side="left", padx=4, pady=8)

        ctk.CTkButton(btns, text="Clear", command=self.clear_log, width=70).pack(
            side="right", padx=4, pady=8
        )
        ctk.CTkButton(btns, text="Gem log", command=self.save_log, width=90).pack(
            side="right", padx=4, pady=8
        )

        # Tools row
        tools = ctk.CTkFrame(self)
        tools.pack(fill="x", **pad)
        ctk.CTkLabel(tools, text="Værktøj").pack(side="left", padx=8)
        self.btn_build = ctk.CTkButton(tools, text="Build", command=self.do_build, width=90)
        self.btn_clean = ctk.CTkButton(tools, text="Clean", command=self.do_clean, width=90)
        self.btn_rebuild = ctk.CTkButton(tools, text="Rebuild", command=self.do_rebuild, width=90)
        self.btn_nina = ctk.CTkButton(
            tools, text="NINA + SSL", command=self.do_nina_ssl, width=110
        )
        self.btn_secrets = ctk.CTkButton(
            tools, text="Secrets…", command=self.do_secrets, width=100
        )
        for b in (
            self.btn_build,
            self.btn_clean,
            self.btn_rebuild,
            self.btn_nina,
            self.btn_secrets,
        ):
            b.pack(side="left", padx=4, pady=6)

        # Visning (projektor)
        view = ctk.CTkFrame(self)
        view.pack(fill="x", **pad)
        ctk.CTkLabel(view, text="Visning").pack(side="left", padx=8)
        self.theme_var = tk.StringVar(value=self._theme)
        ctk.CTkSegmentedButton(
            view,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self._on_theme_change,
            width=160,
        ).pack(side="left", padx=6, pady=6)
        ctk.CTkLabel(view, text="Font").pack(side="left", padx=(16, 4))
        self.font_var = tk.StringVar(value=str(self._font_size))
        ctk.CTkOptionMenu(
            view,
            values=[str(s) for s in FONT_SIZES],
            variable=self.font_var,
            command=self._on_font_change,
            width=80,
        ).pack(side="left", padx=4, pady=6)

        self._action_buttons = [
            self.btn_upload,
            self.btn_monitor,
            self.btn_both,
            self.btn_build,
            self.btn_clean,
            self.btn_rebuild,
            self.btn_nina,
        ]

        self.log = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family="Consolas", size=self._font_size)
        )
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.status_var = tk.StringVar(value="Klar")
        ctk.CTkLabel(self, textvariable=self.status_var, anchor="w").pack(
            fill="x", padx=12, pady=(0, 8)
        )

        self.project_var.trace_add("write", lambda *_: self.after(400, self._reload_envs_debounced))
        self._env_reload_token = 0

    # --- settings ---

    def _load_settings_data(self) -> None:
        """Læs settings før UI (theme/font/favorites/project)."""
        self._settings_project: str | None = (
            str(DEFAULT_PROJECT) if DEFAULT_PROJECT.is_dir() else None
        )
        if not SETTINGS_PATH.is_file():
            return
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        theme = data.get("theme")
        if theme in ("dark", "light"):
            self._theme = theme
        try:
            fs = int(data.get("font_size", self._font_size))
            if fs in FONT_SIZES:
                self._font_size = fs
        except (TypeError, ValueError):
            pass
        favs = data.get("favorites")
        if isinstance(favs, list) and favs:
            cleaned = []
            for f in favs:
                if isinstance(f, dict) and f.get("name") and f.get("path"):
                    if Path(f["path"]).is_dir():
                        cleaned.append({"name": str(f["name"]), "path": str(f["path"])})
            if cleaned:
                self._favorites = cleaned
        p = data.get("project")
        if p and Path(p).is_dir():
            self._settings_project = p

    def _apply_project_from_settings(self) -> None:
        if self._settings_project:
            self.project_var.set(self._settings_project)
            self._reload_envs()

    def _save_settings(self) -> None:
        try:
            SETTINGS_PATH.write_text(
                json.dumps(
                    {
                        "project": self.project_var.get(),
                        "theme": self._theme,
                        "font_size": self._font_size,
                        "favorites": self._favorites,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _on_theme_change(self, value: str) -> None:
        self._theme = value if value in ("dark", "light") else "dark"
        ctk.set_appearance_mode(self._theme)
        self._apply_log_tags()
        self._save_settings()

    def _on_font_change(self, value: str) -> None:
        try:
            size = int(value)
        except ValueError:
            return
        if size not in FONT_SIZES:
            return
        self._font_size = size
        self._apply_font()
        self._save_settings()

    def _apply_font(self) -> None:
        self.log.configure(font=ctk.CTkFont(family="Consolas", size=self._font_size))

    def _apply_log_tags(self) -> None:
        idx = 0 if self._theme == "dark" else 1
        for tag, colors in TAG_COLORS.items():
            try:
                self.log.tag_config(tag, foreground=colors[idx])
            except Exception:
                pass

    def _rebuild_favorite_buttons(self) -> None:
        for b in self._fav_buttons:
            b.destroy()
        self._fav_buttons.clear()
        for fav in self._favorites:
            name = fav["name"]
            path = fav["path"]
            btn = ctk.CTkButton(
                self.fav_frame,
                text=name,
                width=max(90, min(140, 12 * len(name))),
                command=lambda p=path: self.open_favorite(p),
            )
            btn.pack(side="left", padx=3, pady=2)
            self._fav_buttons.append(btn)

    def open_favorite(self, path: str) -> None:
        if not Path(path).is_dir():
            messagebox.showwarning(APP_TITLE, f"Mappen findes ikke:\n{path}")
            return
        self.project_var.set(path)
        self._reload_envs()
        self._save_settings()
        self._log(f"Favorit: {path}")

    def add_favorite(self) -> None:
        project = self.project_var.get().strip()
        if not project or not (Path(project) / "platformio.ini").is_file():
            messagebox.showwarning(APP_TITLE, "Vælg et PlatformIO-projekt først.")
            return
        path = str(Path(project).resolve())
        for f in self._favorites:
            if Path(f["path"]).resolve() == Path(path):
                messagebox.showinfo(APP_TITLE, "Allerede i favoritter.")
                return
        name = Path(path).name
        self._favorites.append({"name": name, "path": path})
        self._rebuild_favorite_buttons()
        self._save_settings()
        self._log(f"Tilføjet favorit: {name}")

    def remove_favorite(self) -> None:
        project = self.project_var.get().strip()
        if not project:
            return
        key = str(Path(project).resolve()).lower()
        before = len(self._favorites)
        self._favorites = [
            f for f in self._favorites if str(Path(f["path"]).resolve()).lower() != key
        ]
        if len(self._favorites) == before:
            messagebox.showinfo(APP_TITLE, "Aktuelt projekt er ikke i favoritter.")
            return
        self._rebuild_favorite_buttons()
        self._save_settings()
        self._log("Favorit fjernet")

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
        tag = classify_line(line)
        if tag:
            self.log.insert("end", line + "\n", tags=tag)
        else:
            self.log.insert("end", line + "\n")
        self.log.see("end")

    def _log_threadsafe(self, line: str) -> None:
        self.after(0, lambda l=line: self._log(l))

    def clear_log(self) -> None:
        self.log.delete("1.0", "end")

    def save_log(self) -> None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        path = filedialog.asksaveasfilename(
            title="Gem log",
            defaultextension=".txt",
            initialfile=f"arduino-starter-log-{stamp}.txt",
            filetypes=[("Tekst", "*.txt"), ("Alle filer", "*.*")],
        )
        if not path:
            return
        try:
            Path(path).write_text(self.log.get("1.0", "end"), encoding="utf-8")
            self._log(f"Log gemt: {path}")
            self.set_status("Log gemt")
        except OSError as e:
            messagebox.showerror(APP_TITLE, f"Kunne ikke gemme log: {e}")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        for btn in self._action_buttons:
            btn.configure(state=state)

    def _selected_port_device(self) -> str | None:
        label = self.port_var.get()
        if not label or label in ("—", "Ingen porte"):
            return None
        return self._port_map.get(label, label.split(" — ")[0].strip())

    def _selected_baud(self) -> int:
        try:
            return int(self.baud_var.get().strip())
        except ValueError:
            return 9600

    def _require_project_env(self, need_port: bool = False) -> tuple[str, str, str | None] | None:
        project = self.project_var.get().strip()
        env = self.env_var.get().strip()
        port = self._selected_port_device()
        if not project or not (Path(project) / "platformio.ini").is_file():
            messagebox.showwarning(APP_TITLE, "Vælg en mappe med platformio.ini.")
            return None
        if not env or env == "—":
            messagebox.showwarning(APP_TITLE, "Vælg et environment.")
            return None
        if need_port and not port:
            messagebox.showwarning(APP_TITLE, "Vælg en COM-port.")
            return None
        if not self._pio:
            self._pio = find_pio()
        if not self._pio:
            messagebox.showerror(APP_TITLE, "PlatformIO CLI ikke fundet.")
            return None
        return project, env, port

    def _ensure_secrets_before_upload(self, project: str) -> bool:
        from secrets_editor import find_secrets_example, migrate_secrets_to_schema

        path = find_secrets_path(project)
        example = find_secrets_example(project)
        # Projekter uden secrets-fil/example (rent offline) — tillad upload
        if path is None and example is None:
            return True
        if path is None:
            if messagebox.askyesno(
                APP_TITLE,
                "Secrets-fil mangler (secrets.h / Secrets.h).\n"
                "Opret fra .example og redigér nu?",
            ):
                ensure_secrets_file(project)
                open_secrets_dialog(self, project)
                path = find_secrets_path(project)
            if path is None:
                messagebox.showerror(APP_TITLE, "Upload blokeret — secrets-fil mangler.")
                return False
        if migrate_secrets_to_schema(project):
            path = find_secrets_path(project)
            self._log(f"Secrets migreret til projektets .example-skema ({path})")
        if path is None or not secrets_looks_valid(path, project):
            self._log(f"ADVARSEL: secrets ser ufuldstændig ud ({path})")
            if messagebox.askyesno(
                APP_TITLE,
                "SSID mangler eller er placeholder "
                "(fx DIT_WIFI / SECRET_SSID).\n\nRedigér secrets før upload?",
            ):
                open_secrets_dialog(self, project)
                path = find_secrets_path(project)
                if path is None or not secrets_looks_valid(path, project):
                    messagebox.showerror(
                        APP_TITLE, "Upload blokeret — udfyld SSID (og øvrige secrets)."
                    )
                    return False
        return True

    # --- project / ports ---

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
        if self.env_var.get() not in names:
            self.env_var.set(names[0])
        self._on_env_change(self.env_var.get())

    def _on_env_change(self, name: str) -> None:
        if name in self._envs:
            self.baud_var.set(str(self._envs[name]))

    def refresh_ports(self, auto_select: bool = False) -> None:
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

        chosen = None
        best = pick_best_port(ports)
        if auto_select and best:
            chosen = best.label
            self._log(f"Auto-valgt {best.label}")
        if not chosen and prev:
            for lab, dev in self._port_map.items():
                if dev.upper() == prev.upper():
                    chosen = lab
                    break
        if not chosen and best:
            chosen = best.label
        if not chosen:
            chosen = labels[0]
        self.port_var.set(chosen)
        for p in ports:
            if p.is_bootloader:
                self._log(f"Tip: {p.device} er i bootloader-mode")

    def auto_select_port(self) -> None:
        ports = list_ports()
        self.refresh_ports(auto_select=False)
        best = pick_best_port(ports)
        if not best:
            messagebox.showwarning(
                APP_TITLE,
                "Ingen Arduino/MKR-port fundet.\n"
                "(Bluetooth-COM ignoreres — tilslut boardet og prøv igen.)",
            )
            return
        self.port_var.set(best.label)
        self._log(f"Auto-valgt {best.label}")
        self.set_status(f"Port: {best.device}")

    # --- actions ---

    def do_upload(self) -> None:
        self._start_upload_job(monitor=False)

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
        self._start_upload_job(monitor=True)

    def do_stop_monitor(self) -> None:
        self._monitor.stop()
        self.set_status("Monitor stoppet")

    def do_build(self) -> None:
        self._start_pio_job(["build"], status="Bygger…")

    def do_clean(self) -> None:
        self._start_pio_job(["clean"], status="Clean…")

    def do_rebuild(self) -> None:
        self._start_pio_job(["clean", "build"], status="Rebuild…")

    def do_secrets(self) -> None:
        project = self.project_var.get().strip()
        if not project or not Path(project).is_dir():
            messagebox.showwarning(APP_TITLE, "Vælg et projekt først.")
            return
        if open_secrets_dialog(self, project):
            self._log(f"Secrets.h gemt for {project}")
            self.set_status("Secrets gemt")

    def do_nina_ssl(self) -> None:
        if self._busy:
            return
        port = self._selected_port_device()
        if not port:
            messagebox.showwarning(APP_TITLE, "Vælg en COM-port.")
            return
        if not UPDATE_DEVICE_PS1.is_file():
            messagebox.showerror(APP_TITLE, f"Mangler script:\n{UPDATE_DEVICE_PS1}")
            return
        if not messagebox.askyesno(
            APP_TITLE,
            "Flasher NINA-firmware + SSL-certifikater.\n"
            "Luk andre Serial Monitors. Fortsæt?",
        ):
            return

        self._save_settings()
        self._set_busy(True)
        self.set_status("NINA + SSL…")

        def worker() -> None:
            try:
                if self._monitor.is_running:
                    self._log_threadsafe("Stopper monitor før NINA-update…")
                    self._monitor.stop()
                    time.sleep(0.5)
                code = run_powershell(
                    UPDATE_DEVICE_PS1,
                    ["-Port", port, "-SkipSketch"],
                    self._log_threadsafe,
                )
                if code != 0:
                    self._log_threadsafe(f"NINA+SSL fejlede (exit {code})")
                    self.after(0, lambda: self.set_status(f"Fejl (exit {code})"))
                else:
                    self._log_threadsafe("NINA + SSL færdig")
                    self.after(0, lambda: self.set_status("NINA + SSL OK"))
                self.after(0, lambda: self.refresh_ports(auto_select=True))
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def _on_monitor_stopped(self) -> None:
        self.after(0, lambda: self.set_status("Klar") if not self._busy else None)

    def _start_pio_job(self, steps: list[str], status: str) -> None:
        """steps: 'build' | 'clean' — rebuild = clean then build."""
        if self._busy:
            return
        req = self._require_project_env(need_port=False)
        if not req:
            return
        project, env, _port = req
        self._save_settings()
        self._set_busy(True)
        self.set_status(status)

        def worker() -> None:
            try:
                code = 0
                for step in steps:
                    if step == "clean":
                        code = run_pio(
                            project, env, self._log_threadsafe, targets=["clean"], pio_path=self._pio
                        )
                    elif step == "build":
                        code = run_pio(
                            project, env, self._log_threadsafe, targets=None, pio_path=self._pio
                        )
                    if code != 0:
                        self._log_threadsafe(f"{step} fejlede (exit {code})")
                        self.after(0, lambda c=code: self.set_status(f"Fejl (exit {c})"))
                        return
                self._log_threadsafe("Job OK")
                self.after(0, lambda: self.set_status("Klar"))
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def _start_upload_job(self, monitor: bool) -> None:
        if self._busy:
            return
        req = self._require_project_env(need_port=True)
        if not req:
            return
        project, env, port = req
        assert port is not None

        if not self._ensure_secrets_before_upload(project):
            return

        self._save_settings()
        self._set_busy(True)
        baud = self._selected_baud()

        def worker() -> None:
            try:
                if self._monitor.is_running:
                    self._log_threadsafe("Stopper monitor før upload…")
                    self._monitor.stop()
                    time.sleep(0.5)

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
                self.after(0, lambda: self.refresh_ports(auto_select=True))

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
