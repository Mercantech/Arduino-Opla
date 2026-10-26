"""Find, parse og redigér Secrets.h (WIFI_SSID / WIFI_PASSWORD)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

_DEFINE_RE = re.compile(
    r'^\s*#\s*define\s+(WIFI_SSID|WIFI_PASSWORD)\s+"((?:\\.|[^"\\])*)"',
    re.MULTILINE,
)


def find_secrets_path(project_dir: str | Path) -> Path | None:
    root = Path(project_dir)
    for rel in ("src/Secrets.h", "Secrets.h", "include/Secrets.h"):
        p = root / rel
        if p.is_file():
            return p
    return None


def find_secrets_example(project_dir: str | Path) -> Path | None:
    root = Path(project_dir)
    for rel in ("src/Secrets.h.example", "Secrets.h.example"):
        p = root / rel
        if p.is_file():
            return p
    return None


def default_secrets_path(project_dir: str | Path) -> Path:
    root = Path(project_dir)
    if (root / "src").is_dir():
        return root / "src" / "Secrets.h"
    return root / "Secrets.h"


def read_secrets(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    ssid, password = "", ""
    for m in _DEFINE_RE.finditer(text):
        key, val = m.group(1), m.group(2)
        val = val.replace('\\"', '"').replace("\\\\", "\\")
        if key == "WIFI_SSID":
            ssid = val
        else:
            password = val
    return ssid, password


def write_secrets(path: Path, ssid: str, password: str) -> None:
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    content = (
        "#pragma once\n\n"
        "// Genereret af Arduino Starter — Secrets.h er gitignored\n"
        f'#define WIFI_SSID "{esc(ssid)}"\n'
        f'#define WIFI_PASSWORD "{esc(password)}"\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ensure_secrets_file(project_dir: str | Path) -> Path | None:
    """Returnér Secrets.h-sti. Kopiér fra .example hvis nødvendigt."""
    existing = find_secrets_path(project_dir)
    if existing:
        return existing
    example = find_secrets_example(project_dir)
    dest = default_secrets_path(project_dir)
    if example:
        shutil.copy2(example, dest)
        return dest
    return None


def secrets_looks_valid(path: Path) -> bool:
    try:
        ssid, _ = read_secrets(path)
    except OSError:
        return False
    return bool(ssid.strip()) and ssid.strip() not in ("dit-wifi-navn", "your-ssid")


class SecretsDialog(ctk.CTkToplevel):
    """Modal dialog til WiFi SSID/password."""

    def __init__(self, master, project_dir: str | Path, title: str = "Secrets.h"):
        super().__init__(master)
        self.title(title)
        self.geometry("420x240")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.project_dir = Path(project_dir)
        self.result_saved = False
        self._path = find_secrets_path(self.project_dir) or default_secrets_path(
            self.project_dir
        )

        ssid, password = "", ""
        if self._path.is_file():
            try:
                ssid, password = read_secrets(self._path)
            except OSError:
                pass

        ctk.CTkLabel(self, text=str(self._path), text_color="gray").pack(
            anchor="w", padx=16, pady=(12, 4)
        )

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(form, text="WiFi SSID").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.ssid_var = tk.StringVar(value=ssid)
        ctk.CTkEntry(form, textvariable=self.ssid_var, width=260).grid(
            row=0, column=1, padx=6, pady=6
        )

        ctk.CTkLabel(form, text="Password").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.pw_var = tk.StringVar(value=password)
        self.pw_entry = ctk.CTkEntry(form, textvariable=self.pw_var, width=260, show="*")
        self.pw_entry.grid(row=1, column=1, padx=6, pady=6)

        self._show_pw = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            form, text="Vis", variable=self._show_pw, command=self._toggle_pw, width=60
        ).grid(row=1, column=2, padx=4)

        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=16, pady=12)
        ctk.CTkButton(btns, text="Annuller", width=100, command=self.destroy).pack(
            side="right", padx=6
        )
        ctk.CTkButton(btns, text="Gem", width=100, command=self._save).pack(
            side="right", padx=6
        )

        self.after(50, self.lift)
        self.after(60, self.focus_force)

    def _toggle_pw(self) -> None:
        self.pw_entry.configure(show="" if self._show_pw.get() else "*")

    def _save(self) -> None:
        ssid = self.ssid_var.get().strip()
        password = self.pw_var.get()
        if not ssid:
            messagebox.showwarning("Secrets.h", "SSID må ikke være tom.", parent=self)
            return
        try:
            write_secrets(self._path, ssid, password)
        except OSError as e:
            messagebox.showerror("Secrets.h", f"Kunne ikke gemme: {e}", parent=self)
            return
        self.result_saved = True
        self.destroy()


def open_secrets_dialog(master, project_dir: str | Path) -> bool:
    """Åbn editor. Returnerer True hvis gemt."""
    path = ensure_secrets_file(project_dir)
    if path is None:
        # Opret tom skabelon
        path = default_secrets_path(project_dir)
        write_secrets(path, "", "")

    dlg = SecretsDialog(master, project_dir)
    master.wait_window(dlg)
    return dlg.result_saved
