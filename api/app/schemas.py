from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DeviceIn(BaseModel):
    samd_id: str = Field(min_length=8, max_length=64)
    mac: str | None = None
    ecc_serial: str | None = None
    label: str | None = None


class TestReportIn(BaseModel):
    passed: bool
    passed_count: int = 0
    failed_count: int = 0
    details: str | None = None
    report: dict[str, Any] | None = None


class TestReportOut(BaseModel):
    id: int
    samd_id: str
    passed: bool
    passed_count: int
    failed_count: int
    details: str | None
    report: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeviceOut(BaseModel):
    """id = SAMD chip-ID (enhedens unikke ID)."""

    id: str
    samd_id: str
    mac: str | None
    ecc_serial: str | None
    label: str | None
    created_at: datetime
    updated_at: datetime
    tests: list[TestReportOut] = []
    test_count: int = 0
    last_passed: bool | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_device(cls, device: object) -> "DeviceOut":
        import json

        raw_tests = list(device.tests or [])  # type: ignore[attr-defined]
        raw_tests.sort(key=lambda t: t.created_at, reverse=True)

        tests_out: list[TestReportOut] = []
        for t in raw_tests:
            report = None
            details = t.details
            if details:
                try:
                    parsed = json.loads(details)
                    if isinstance(parsed, dict):
                        report = parsed.get("report", parsed)
                except json.JSONDecodeError:
                    report = None
            tests_out.append(
                TestReportOut(
                    id=t.id,
                    samd_id=t.samd_id,
                    passed=t.passed,
                    passed_count=t.passed_count,
                    failed_count=t.failed_count,
                    details=details,
                    report=report,
                    created_at=t.created_at,
                )
            )

        last_passed = tests_out[0].passed if tests_out else None
        return cls(
            id=device.samd_id,  # type: ignore[attr-defined]
            samd_id=device.samd_id,  # type: ignore[attr-defined]
            mac=device.mac,  # type: ignore[attr-defined]
            ecc_serial=device.ecc_serial,  # type: ignore[attr-defined]
            label=device.label,  # type: ignore[attr-defined]
            created_at=device.created_at,  # type: ignore[attr-defined]
            updated_at=device.updated_at,  # type: ignore[attr-defined]
            tests=tests_out,
            test_count=len(tests_out),
            last_passed=last_passed,
        )
