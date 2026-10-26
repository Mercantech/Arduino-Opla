"""Klassificér loglinjer til farvetags (pass/fail)."""
from __future__ import annotations

import re

# Tag-navne brugt i CTkTextbox
TAG_OK = "ok"
TAG_FAIL = "fail"
TAG_SUMMARY = "summary"
TAG_WARN = "warn"
TAG_INFO = "info"

# (tag, hex for dark theme, hex for light theme)
TAG_COLORS = {
    TAG_OK: ("#3dd68c", "#1a7f4b"),
    TAG_FAIL: ("#ff6b6b", "#c62828"),
    TAG_SUMMARY: ("#7eb6ff", "#1565c0"),
    TAG_WARN: ("#ffd166", "#e65100"),
    TAG_INFO: ("#c8c8c8", "#424242"),
}

_FAIL = re.compile(
    r"(?i)(\bFEJL\b|\bFAIL\b|\bFAILED\b|fejlede|error:|Upload fejlede|"
    r"Tests FEJL|touched=0/|\bERROR\b)"
)
_OK = re.compile(
    r"(?i)(:\s*OK\b|\bOK\b\s*$|SUCCESS|Upload OK|Job OK|NINA \+ SSL (OK|færdig)|"
    r"enhed registreret|Bestået:\s*[1-9])"
)
_SUMMARY = re.compile(
    r"(?i)(Test-opsummering|=== Test|Bestået:|Fejlet:|Hardware OK|Alle tests)"
)
_WARN = re.compile(
    r"(?i)(ADVARSEL|WARN|bootloader|Tip:|Secrets\.h|placeholder|Bluetooth)"
)


def classify_line(line: str) -> str | None:
    """Returnér tag-navn eller None (standard tekst)."""
    if not line or not line.strip():
        return None
    if _SUMMARY.search(line):
        return TAG_SUMMARY
    if _FAIL.search(line):
        return TAG_FAIL
    if _OK.search(line):
        return TAG_OK
    if _WARN.search(line):
        return TAG_WARN
    return None
