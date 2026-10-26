"""Generisk secrets-editor til PlatformIO-projekter (Secrets.h / secrets.h / …)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# Alle string-#define i secrets-filer
_STRING_DEFINE_RE = re.compile(
    r'^(\s*#\s*define\s+)([A-Za-z_][A-Za-z0-9_]*)(\s+)"((?:\\.|[^"\\])*)"',
    re.MULTILINE,
)

_CANDIDATE_NAMES = (
    "secrets.h",
    "Secrets.h",
    "arduino_secrets.h",
    "ArduinoSecrets.h",
)
_SEARCH_DIRS = ("src", "include", ".")

_PLACEHOLDERS = frozenset(
    {
        "",
        "dit-wifi-navn",
        "din-wifi-kode",
        "your-ssid",
        "your-password",
        "DIT_WIFI",
        "DIT_PASSWORD",
        "SKIFT_MIG",
        "changeme",
        "CHANGE_ME",
        "password",
        "ssid",
    }
)

# Alias når Starter tidligere skrev WIFI_* ind i et SECRET_*-projekt
_KEY_ALIASES = {
    "SECRET_SSID": ("WIFI_SSID", "SSID"),
    "SECRET_PASS": ("WIFI_PASSWORD", "WIFI_PASS", "PASSWORD"),
    "WIFI_SSID": ("SECRET_SSID", "SSID"),
    "WIFI_PASSWORD": ("SECRET_PASS", "WIFI_PASS", "PASSWORD"),
    "WIFI_PASS": ("SECRET_PASS", "WIFI_PASSWORD", "PASSWORD"),
}


def _unescape(val: str) -> str:
    return val.replace('\\"', '"').replace("\\\\", "\\")


def _escape(val: str) -> str:
    return val.replace("\\", "\\\\").replace('"', '\\"')


def _looks_password_key(key: str) -> bool:
    u = key.upper()
    if "SSID" in u:
        return False
    return any(
        x in u
        for x in ("PASSWORD", "PASS", "PWD", "TOKEN", "API_KEY", "APIKEY", "SECRET_KEY")
    )


def _looks_ssid_key(key: str) -> bool:
    return "SSID" in key.upper()


def _iter_candidate_paths(project_dir: Path, suffix: str = "") -> list[Path]:
    """suffix='' → secrets.h; suffix='.example' → secrets.h.example"""
    out: list[Path] = []
    for d in _SEARCH_DIRS:
        base = project_dir if d == "." else project_dir / d
        if not base.is_dir() and d != ".":
            continue
        for name in _CANDIDATE_NAMES:
            out.append(base / f"{name}{suffix}")
    return out


def find_secrets_path(project_dir: str | Path) -> Path | None:
    root = Path(project_dir)
    for p in _iter_candidate_paths(root):
        if p.is_file():
            return p
    return None


def find_secrets_example(project_dir: str | Path) -> Path | None:
    root = Path(project_dir)
    for p in _iter_candidate_paths(root, suffix=".example"):
        if p.is_file():
            return p
    return None


def default_secrets_path(project_dir: str | Path) -> Path:
    """Foretræk samme filnavn som .example (secrets.h vs Secrets.h)."""
    root = Path(project_dir)
    example = find_secrets_example(root)
    if example:
        # secrets.h.example → secrets.h
        name = example.name[: -len(".example")]
        return example.parent / name
    if (root / "src").is_dir():
        return root / "src" / "secrets.h"
    return root / "secrets.h"


def parse_string_defines(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    out: dict[str, str] = {}
    for m in _STRING_DEFINE_RE.finditer(text):
        out[m.group(2)] = _unescape(m.group(4))
    return out


def schema_keys(project_dir: str | Path) -> list[str]:
    """Ordnet liste af makro-navne (fra example, ellers eksisterende fil)."""
    example = find_secrets_example(project_dir)
    if example:
        return list(parse_string_defines(example).keys())
    existing = find_secrets_path(project_dir)
    if existing:
        keys = list(parse_string_defines(existing).keys())
        if keys:
            return keys
    return ["WIFI_SSID", "WIFI_PASSWORD"]


def load_secret_values(project_dir: str | Path) -> dict[str, str]:
    """Værdier til schema — med alias-fallback (WIFI_* ↔ SECRET_*)."""
    keys = schema_keys(project_dir)
    raw: dict[str, str] = {}
    path = find_secrets_path(project_dir)
    if path:
        raw = parse_string_defines(path)
    # Hvis filen er “forkert skrevet” af gammel Starter, læs også den som er
    values: dict[str, str] = {}
    for key in keys:
        if key in raw and raw[key].strip():
            values[key] = raw[key]
            continue
        for alt in _KEY_ALIASES.get(key, ()):
            if alt in raw and raw[alt].strip():
                values[key] = raw[alt]
                break
        else:
            values[key] = raw.get(key, "")
    return values


def write_secret_values(path: Path, values: dict[str, str], template: Path | None = None) -> None:
    """
    Skriv schema-keys til path. Bruger .example som skabelon ved schema-mismatch
    (fx WIFI_* i filen, men projektet forventer SECRET_*), ellers in-place update.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    needed = set(values.keys())
    source: Path | None = None
    if path.is_file():
        have = set(parse_string_defines(path).keys())
        if needed and needed <= have:
            source = path
        elif template and template.is_file():
            source = template
        else:
            source = path
    elif template and template.is_file():
        source = template

    if source and source.is_file():
        text = source.read_text(encoding="utf-8", errors="replace")

        def repl(m: re.Match[str]) -> str:
            key = m.group(2)
            if key not in values:
                return m.group(0)
            return f'{m.group(1)}{key}{m.group(3)}"{_escape(values[key])}"'

        new_text, n = _STRING_DEFINE_RE.subn(repl, text)
        present = set(parse_string_defines(source).keys())
        missing = [k for k in values if k not in present]
        if missing:
            extra = "".join(f'\n#define {k} "{_escape(values[k])}"' for k in missing)
            if not new_text.endswith("\n"):
                new_text += "\n"
            new_text += extra + "\n"
        elif n == 0 and values:
            lines = [new_text.rstrip(), ""]
            for k, v in values.items():
                lines.append(f'#define {k} "{_escape(v)}"')
            new_text = "\n".join(lines) + "\n"
        path.write_text(new_text, encoding="utf-8")
        return

    lines = [
        "#pragma once",
        "",
        "// Genereret af Arduino Starter (gitignorér denne fil)",
    ]
    for k, v in values.items():
        lines.append(f'#define {k} "{_escape(v)}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_secrets_file(project_dir: str | Path) -> Path | None:
    existing = find_secrets_path(project_dir)
    if existing:
        return existing
    example = find_secrets_example(project_dir)
    dest = default_secrets_path(project_dir)
    if example:
        shutil.copy2(example, dest)
        return dest
    return None


def secrets_looks_valid(path: Path, project_dir: str | Path | None = None) -> bool:
    """SSID skal være sat; øvrige felter må ikke være placeholders (tom MQTT o.l. er OK)."""
    try:
        if project_dir:
            values = load_secret_values(project_dir)
        else:
            values = parse_string_defines(path)
    except OSError:
        return False
    if not values:
        return False
    placeholders = {p.lower() for p in _PLACEHOLDERS}
    ssid_keys = [k for k in values if _looks_ssid_key(k)]
    if ssid_keys:
        for k in ssid_keys:
            v = values.get(k, "").strip()
            if not v or v.lower() in placeholders:
                return False
    else:
        # Ingen SSID-key — kræv mindst én ikke-tom, ikke-placeholder værdi
        if not any(
            v.strip() and v.strip().lower() not in placeholders for v in values.values()
        ):
            return False
    for v in values.values():
        s = v.strip()
        if s and s.lower() in placeholders:
            return False
    return True


def migrate_secrets_to_schema(project_dir: str | Path) -> bool:
    """
    Hvis secrets-fil mangler keys fra .example: omskriv til example-skema
    og bevar værdier via alias. Returnerer True hvis der blev skrevet.
    """
    root = Path(project_dir)
    if not secrets_schema_mismatch(root):
        return False
    example = find_secrets_example(root)
    dest = find_secrets_path(root) or default_secrets_path(root)
    if not example:
        return False
    old_vals = load_secret_values(root)
    write_secret_values(dest, old_vals, template=example)
    return True


def secrets_schema_mismatch(project_dir: str | Path) -> bool:
    """True hvis secrets-fil mangler keys fra .example (fx kun WIFI_* i SECRET_*-projekt)."""
    example = find_secrets_example(project_dir)
    path = find_secrets_path(project_dir)
    if not example or not path:
        return False
    needed = set(parse_string_defines(example).keys())
    have = set(parse_string_defines(path).keys())
    return bool(needed - have)


class SecretsDialog(ctk.CTkToplevel):
    """Dynamisk dialog for alle string-#define i projektets secrets-fil."""

    def __init__(self, master, project_dir: str | Path, title: str = "Secrets"):
        super().__init__(master)
        self.title(title)
        self.geometry("520x360")
        self.minsize(480, 280)
        self.transient(master)
        self.grab_set()

        self.project_dir = Path(project_dir)
        self.result_saved = False
        self._path = find_secrets_path(self.project_dir) or default_secrets_path(
            self.project_dir
        )
        self._example = find_secrets_example(self.project_dir)
        self._keys = schema_keys(self.project_dir)
        values = load_secret_values(self.project_dir)

        ctk.CTkLabel(self, text=str(self._path), text_color="gray").pack(
            anchor="w", padx=16, pady=(12, 2)
        )
        if self._example:
            ctk.CTkLabel(
                self,
                text=f"Skema fra {self._example.name}",
                text_color="gray",
            ).pack(anchor="w", padx=16, pady=(0, 6))

        form = ctk.CTkScrollableFrame(self, height=220)
        form.pack(fill="both", expand=True, padx=16, pady=4)

        self._vars: dict[str, tk.StringVar] = {}
        self._entries: dict[str, ctk.CTkEntry] = {}
        self._show_flags: dict[str, tk.BooleanVar] = {}

        for row, key in enumerate(self._keys):
            ctk.CTkLabel(form, text=key, width=160, anchor="w").grid(
                row=row, column=0, sticky="w", padx=6, pady=5
            )
            var = tk.StringVar(value=values.get(key, ""))
            self._vars[key] = var
            show = "*" if _looks_password_key(key) else ""
            entry = ctk.CTkEntry(form, textvariable=var, width=260, show=show)
            entry.grid(row=row, column=1, padx=6, pady=5)
            self._entries[key] = entry
            if _looks_password_key(key):
                flag = tk.BooleanVar(value=False)
                self._show_flags[key] = flag
                ctk.CTkCheckBox(
                    form,
                    text="Vis",
                    variable=flag,
                    width=50,
                    command=lambda k=key: self._toggle_pw(k),
                ).grid(row=row, column=2, padx=4)

        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=16, pady=12)
        if self._example:
            ctk.CTkButton(
                btns,
                text="Nulstil fra example",
                width=140,
                command=self._reset_from_example,
            ).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Annuller", width=100, command=self.destroy).pack(
            side="right", padx=6
        )
        ctk.CTkButton(btns, text="Gem", width=100, command=self._save).pack(
            side="right", padx=6
        )

        self.after(50, self.lift)
        self.after(60, self.focus_force)

    def _toggle_pw(self, key: str) -> None:
        entry = self._entries.get(key)
        flag = self._show_flags.get(key)
        if entry and flag is not None:
            entry.configure(show="" if flag.get() else "*")

    def _reset_from_example(self) -> None:
        if not self._example:
            return
        if not messagebox.askyesno(
            "Secrets",
            "Nulstil filen til .example-skema?\n"
            "Udfyldte værdier forsøges bevaret via alias (WIFI_* → SECRET_*).",
            parent=self,
        ):
            return
        old_vals = {k: self._vars[k].get() for k in self._keys}
        # Inkluder også rå fil-værdier til alias-mapping
        if self._path.is_file():
            old_vals = {**parse_string_defines(self._path), **old_vals}
        shutil.copy2(self._example, self._path)
        merged = load_secret_values(self.project_dir)
        for k, v in old_vals.items():
            if k in merged and v.strip():
                merged[k] = v
            else:
                for schema_key, alts in _KEY_ALIASES.items():
                    if schema_key in merged and k in alts and v.strip():
                        if not merged[schema_key].strip():
                            merged[schema_key] = v
        write_secret_values(self._path, merged, template=self._example)
        # Genindlæs felter
        self._keys = schema_keys(self.project_dir)
        fresh = load_secret_values(self.project_dir)
        for k, var in self._vars.items():
            if k in fresh:
                var.set(fresh[k])
        messagebox.showinfo("Secrets", "Skema nulstillet — tjek felterne og Gem.", parent=self)

    def _save(self) -> None:
        values = {k: self._vars[k].get() for k in self._keys}
        ssid_keys = [k for k in self._keys if "SSID" in k.upper()]
        for k in ssid_keys:
            if not values.get(k, "").strip():
                messagebox.showwarning(
                    "Secrets", f"{k} må ikke være tom.", parent=self
                )
                return
        try:
            write_secret_values(self._path, values, template=self._example)
        except OSError as e:
            messagebox.showerror("Secrets", f"Kunne ikke gemme: {e}", parent=self)
            return
        self.result_saved = True
        self.destroy()


def open_secrets_dialog(master, project_dir: str | Path) -> bool:
    """Åbn editor. Returnerer True hvis gemt."""
    path = ensure_secrets_file(project_dir)
    if path is None:
        path = default_secrets_path(project_dir)
        keys = schema_keys(project_dir)
        write_secret_values(path, {k: "" for k in keys})

    # Auto-migrér WIFI_* → SECRET_* (eller omvendt) uden at spørge — værdier bevares
    if secrets_schema_mismatch(project_dir):
        migrate_secrets_to_schema(project_dir)

    dlg = SecretsDialog(master, project_dir)
    master.wait_window(dlg)
    return dlg.result_saved
