"""Find PlatformIO CLI, parse platformio.ini, kør upload med live log."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

LogFn = Callable[[str], None]


@dataclass
class PioEnv:
    name: str
    monitor_speed: int = 9600
    board: str = ""
    extras: dict[str, str] = field(default_factory=dict)


def find_pio() -> str | None:
    """Returnér sti til platformio/pio executable, eller None."""
    for name in ("platformio", "pio", "platformio.exe", "pio.exe"):
        found = shutil.which(name)
        if found:
            return found

    home = Path.home()
    candidates = [
        home / "AppData/Local/Programs/Python/Python311/Scripts/platformio.exe",
        home / "AppData/Local/Programs/Python/Python312/Scripts/platformio.exe",
        home / "AppData/Local/Programs/Python/Python313/Scripts/platformio.exe",
        home / ".platformio/penv/Scripts/platformio.exe",
        home / ".platformio/penv/Scripts/pio.exe",
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Programs/Python/Python311/Scripts/platformio.exe",
    ]
    for c in candidates:
        if c and c.is_file():
            return str(c)
    return None


def parse_platformio_ini(project_dir: str | Path) -> list[PioEnv]:
    """Parse [env:…] sektioner og monitor_speed."""
    ini = Path(project_dir) / "platformio.ini"
    if not ini.is_file():
        raise FileNotFoundError(f"Ingen platformio.ini i {project_dir}")

    text = ini.read_text(encoding="utf-8", errors="replace")
    envs: list[PioEnv] = []
    current: PioEnv | None = None
    global_baud = 9600

    section_re = re.compile(r"^\[([^\]]+)\]\s*$")

    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        m = section_re.match(line)
        if m:
            if current is not None:
                envs.append(current)
            name = m.group(1).strip()
            if name.startswith("env:"):
                current = PioEnv(name=name[4:], monitor_speed=global_baud)
            else:
                current = None
            continue

        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()

        if current is None:
            if key == "monitor_speed":
                try:
                    global_baud = int(val)
                except ValueError:
                    pass
            continue

        if key == "monitor_speed":
            try:
                current.monitor_speed = int(val)
            except ValueError:
                pass
        elif key == "board":
            current.board = val
        else:
            current.extras[key] = val

    if current is not None:
        envs.append(current)

    return envs


def run_pio(
    project_dir: str | Path,
    env_name: str,
    on_line: LogFn,
    targets: list[str] | None = None,
    upload_port: str | None = None,
    pio_path: str | None = None,
    cancel_event: threading.Event | None = None,
) -> int:
    """
    Kør `pio run -e <env> [-t target…] [--upload-port COMx]`.
    Streamer stdout/stderr linje for linje via on_line.
    Returnerer process exit code.
    """
    pio = pio_path or find_pio()
    if not pio:
        on_line("FEJL: platformio/pio ikke fundet. Installér PlatformIO CLI.")
        return 127

    project_dir = Path(project_dir)
    cmd = [pio, "run", "-e", env_name]
    for t in targets or []:
        cmd.extend(["-t", t])
    if upload_port:
        cmd.extend(["--upload-port", upload_port])

    on_line(f"$ {' '.join(cmd)}")
    on_line(f"cwd: {project_dir}")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

    proc = subprocess.Popen(
        cmd,
        cwd=str(project_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=creationflags,
    )

    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            if cancel_event and cancel_event.is_set():
                proc.terminate()
                on_line("Job afbrudt.")
                break
            on_line(line.rstrip("\r\n"))
    finally:
        try:
            proc.stdout.close()
        except Exception:
            pass

    return proc.wait()


def run_upload(
    project_dir: str | Path,
    env_name: str,
    port: str,
    on_line: LogFn,
    pio_path: str | None = None,
    cancel_event: threading.Event | None = None,
) -> int:
    """Kør `pio run -e <env> -t upload --upload-port <port>`."""
    return run_pio(
        project_dir=project_dir,
        env_name=env_name,
        on_line=on_line,
        targets=["upload"],
        upload_port=port,
        pio_path=pio_path,
        cancel_event=cancel_event,
    )


def run_powershell(
    script_path: str | Path,
    args: list[str],
    on_line: LogFn,
    cancel_event: threading.Event | None = None,
) -> int:
    """Kør et .ps1-script og stream output."""
    script_path = Path(script_path)
    if not script_path.is_file():
        on_line(f"FEJL: script mangler: {script_path}")
        return 127

    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        *args,
    ]
    on_line(f"$ {' '.join(cmd)}")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

    proc = subprocess.Popen(
        cmd,
        cwd=str(script_path.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=creationflags,
    )
    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            if cancel_event and cancel_event.is_set():
                proc.terminate()
                on_line("Script afbrudt.")
                break
            on_line(line.rstrip("\r\n"))
    finally:
        try:
            proc.stdout.close()
        except Exception:
            pass
    return proc.wait()
