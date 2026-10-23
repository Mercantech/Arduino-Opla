import os
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.config import CORS_ORIGINS
from app.db import Base, engine, get_db

app = FastAPI(title="Arduino Opla API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    for attempt in range(30):
        try:
            # Sæt RESET_DB=true én gang ved schema-skift (int-id → samd_id PK)
            if os.getenv("RESET_DB", "false").lower() in ("1", "true", "yes"):
                Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            time.sleep(2)
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "opla-api"}


@app.get("/api/health")
def api_health():
    return health()


@app.get("/api/devices", response_model=list[schemas.DeviceOut])
def list_devices(db: Session = Depends(get_db)):
    devices = (
        db.query(models.Device)
        .options(joinedload(models.Device.tests))
        .order_by(models.Device.updated_at.desc())
        .all()
    )
    return [schemas.DeviceOut.from_device(d) for d in devices]


@app.post("/api/devices", response_model=schemas.DeviceOut)
def upsert_device(body: schemas.DeviceIn, db: Session = Depends(get_db)):
    device = (
        db.query(models.Device)
        .options(joinedload(models.Device.tests))
        .filter(models.Device.samd_id == body.samd_id)
        .first()
    )
    if device is None:
        device = models.Device(samd_id=body.samd_id)
        db.add(device)

    if body.mac is not None:
        device.mac = body.mac
    if body.ecc_serial is not None:
        device.ecc_serial = body.ecc_serial
    if body.label is not None:
        device.label = body.label

    db.commit()
    db.refresh(device)
    return schemas.DeviceOut.from_device(device)


@app.get("/api/devices/{samd_id}", response_model=schemas.DeviceOut)
def get_device(samd_id: str, db: Session = Depends(get_db)):
    device = (
        db.query(models.Device)
        .options(joinedload(models.Device.tests))
        .filter(models.Device.samd_id == samd_id)
        .first()
    )
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return schemas.DeviceOut.from_device(device)


@app.get("/api/devices/{samd_id}/tests", response_model=list[schemas.TestReportOut])
def list_tests(samd_id: str, db: Session = Depends(get_db)):
    """Fuld testhistorik for enheden (nyeste først)."""
    device = (
        db.query(models.Device)
        .options(joinedload(models.Device.tests))
        .filter(models.Device.samd_id == samd_id)
        .first()
    )
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return schemas.DeviceOut.from_device(device).tests


@app.post("/api/devices/{samd_id}/tests", response_model=schemas.TestReportOut)
def add_test(samd_id: str, body: schemas.TestReportIn, db: Session = Depends(get_db)):
    """Tilføj ny testrapport — sletter aldrig gamle (fuld historik)."""
    import json
    from datetime import datetime, timezone

    device = db.query(models.Device).filter(models.Device.samd_id == samd_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    details = body.details
    if body.report is not None:
        details = json.dumps(
            {
                "passed": body.passed,
                "passed_count": body.passed_count,
                "failed_count": body.failed_count,
                "report": body.report,
            },
            ensure_ascii=False,
        )
    elif details is None and body.report is None:
        # Hele body kan være flat JSON fra firmware (report nested i POST)
        details = None

    # Firmware sender {"passed",...,"report":{...}} — gem hele payload hvis details mangler
    if details is None:
        details = json.dumps(body.model_dump(exclude_none=True), ensure_ascii=False)

    row = models.TestReport(
        samd_id=samd_id,
        passed=body.passed,
        passed_count=body.passed_count,
        failed_count=body.failed_count,
        details=details,
    )
    db.add(row)
    device.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)

    parsed_report = body.report
    if parsed_report is None and details:
        try:
            blob = json.loads(details)
            if isinstance(blob, dict):
                parsed_report = blob.get("report", blob)
        except json.JSONDecodeError:
            parsed_report = None

    return schemas.TestReportOut(
        id=row.id,
        samd_id=row.samd_id,
        passed=row.passed,
        passed_count=row.passed_count,
        failed_count=row.failed_count,
        details=row.details,
        report=parsed_report,
        created_at=row.created_at,
    )
