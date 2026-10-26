"""COM-port liste, vent på app-port efter upload, serial reader-tråd."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable

import serial
import serial.tools.list_ports

LogFn = Callable[[str], None]


@dataclass(frozen=True)
class SerialPortInfo:
    device: str
    description: str
    hwid: str
    is_bootloader: bool

    @property
    def label(self) -> str:
        tag = " [bootloader]" if self.is_bootloader else ""
        return f"{self.device} — {self.description}{tag}"


def list_ports() -> list[SerialPortInfo]:
    result: list[SerialPortInfo] = []
    for p in serial.tools.list_ports.comports():
        desc = p.description or "Unknown"
        hwid = p.hwid or ""
        is_boot = "bootloader" in desc.lower()
        result.append(
            SerialPortInfo(
                device=p.device,
                description=desc,
                hwid=hwid,
                is_bootloader=is_boot,
            )
        )

    def sort_key(info: SerialPortInfo):
        # Arduino/MKR først, derefter COM-nummer
        prio = 0 if any(
            x in (info.description + info.hwid)
            for x in ("Arduino", "MKR", "2341", "USB Serial")
        ) else 1
        num = 999
        if info.device.upper().startswith("COM"):
            try:
                num = int(info.device[3:])
            except ValueError:
                pass
        return (prio, num, info.device)

    return sorted(result, key=sort_key)


def wait_for_app_port(
    preferred: str | None = None,
    timeout: float = 25.0,
    poll: float = 0.35,
) -> str | None:
    """
    Efter upload: vent til en ikke-bootloader port er tilbage.
    Foretræk `preferred` hvis den dukker op igen som app-port.
    """
    deadline = time.time() + timeout
    time.sleep(0.8)
    while time.time() < deadline:
        ports = list_ports()
        apps = [p for p in ports if not p.is_bootloader]
        boots = [p for p in ports if p.is_bootloader]

        if preferred:
            for p in apps:
                if p.device.upper() == preferred.upper():
                    return p.device

        # App-port uden bootloader = klar
        if apps and not boots:
            return apps[0].device

        # Begge findes kortvarigt — vælg app
        if apps:
            return apps[0].device

        time.sleep(poll)

    ports = list_ports()
    apps = [p for p in ports if not p.is_bootloader]
    if apps:
        return apps[0].device
    if ports:
        return ports[0].device
    return None


class SerialMonitor:
    """Baggrunds-serial-læser. Kald stop() for at frigøre porten."""

    def __init__(self, on_line: LogFn, on_stopped: Callable[[], None] | None = None):
        self._on_line = on_line
        self._on_stopped = on_stopped
        self._ser: serial.Serial | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.port: str | None = None
        self.baud: int = 9600

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, port: str, baud: int = 9600) -> None:
        if self.is_running:
            self.stop()
            time.sleep(0.3)

        self._stop.clear()
        self.port = port
        self.baud = baud
        try:
            self._ser = serial.Serial(port, baud, timeout=0.25)
        except serial.SerialException as e:
            self._on_line(f"FEJL: kunne ikke åbne {port}: {e}")
            raise

        self._on_line(f"--- monitor {port} @ {baud} ---")
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        t = self._thread
        if t and t.is_alive():
            t.join(timeout=2.0)
        self._thread = None
        ser = self._ser
        self._ser = None
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
            self._on_line("--- monitor stoppet ---")
        if self._on_stopped:
            try:
                self._on_stopped()
            except Exception:
                pass

    def _read_loop(self) -> None:
        ser = self._ser
        if ser is None:
            return
        buf = bytearray()
        try:
            while not self._stop.is_set():
                try:
                    chunk = ser.read(256)
                except serial.SerialException as e:
                    self._on_line(f"Serial fejl: {e}")
                    break
                if not chunk:
                    continue
                buf.extend(chunk)
                while True:
                    nl = buf.find(b"\n")
                    if nl < 0:
                        break
                    line = buf[:nl]
                    del buf[: nl + 1]
                    if line.endswith(b"\r"):
                        line = line[:-1]
                    text = line.decode("utf-8", errors="replace")
                    self._on_line(text)
        finally:
            try:
                if ser and ser.is_open:
                    ser.close()
            except Exception:
                pass
