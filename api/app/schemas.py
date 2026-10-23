from datetime import datetime

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


class TestReportOut(BaseModel):
    id: int
    samd_id: str
    passed: bool
    passed_count: int
    failed_count: int
    details: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeviceOut(BaseModel):
    """id = SAMD chip-ID (enhedens unikke ID)."""

    id: str  # alias for samd_id — klientens primære nøgle
    samd_id: str
    mac: str | None
    ecc_serial: str | None
    label: str | None
    created_at: datetime
    updated_at: datetime
    tests: list[TestReportOut] = []

    model_config = {"from_attributes": True}

    @classmethod
    def from_device(cls, device: object) -> "DeviceOut":
        return cls(
            id=device.samd_id,  # type: ignore[attr-defined]
            samd_id=device.samd_id,  # type: ignore[attr-defined]
            mac=device.mac,  # type: ignore[attr-defined]
            ecc_serial=device.ecc_serial,  # type: ignore[attr-defined]
            label=device.label,  # type: ignore[attr-defined]
            created_at=device.created_at,  # type: ignore[attr-defined]
            updated_at=device.updated_at,  # type: ignore[attr-defined]
            tests=list(device.tests or []),  # type: ignore[attr-defined]
        )
