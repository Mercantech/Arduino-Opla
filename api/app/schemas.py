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
    passed: bool
    passed_count: int
    failed_count: int
    details: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeviceOut(BaseModel):
    id: int
    samd_id: str
    mac: str | None
    ecc_serial: str | None
    label: str | None
    created_at: datetime
    updated_at: datetime
    tests: list[TestReportOut] = []

    model_config = {"from_attributes": True}
