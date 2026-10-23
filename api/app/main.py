import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.config import CORS_ORIGINS
from app.db import Base, engine, get_db

app = FastAPI(title="Arduino Opla API", version="1.0.0")

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
    return (
        db.query(models.Device)
        .options(joinedload(models.Device.tests))
        .order_by(models.Device.updated_at.desc())
        .all()
    )


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
    return device


@app.get("/api/devices/{device_id}", response_model=schemas.DeviceOut)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = (
        db.query(models.Device)
        .options(joinedload(models.Device.tests))
        .filter(models.Device.id == device_id)
        .first()
    )
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.post("/api/devices/{device_id}/tests", response_model=schemas.TestReportOut)
def add_test(device_id: int, body: schemas.TestReportIn, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    report = models.TestReport(
        device_id=device_id,
        passed=body.passed,
        passed_count=body.passed_count,
        failed_count=body.failed_count,
        details=body.details,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
