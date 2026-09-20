from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import Base, engine, SessionLocal
import models
from schemas import TouristCreate, TouristLogin
from auth import verify_password
from ai.risk_engine import calculate_risk

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tourist Safety System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Tourist Safety System API is running"
    }


@app.post("/register")
def register_tourist(
    tourist: TouristCreate,
    db: Session = Depends(get_db)
):
    existing_tourist = (
        db.query(models.Tourist)
        .filter(models.Tourist.email == tourist.email)
        .first()
    )

    if existing_tourist:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = pwd_context.hash(tourist.password)

    new_tourist = models.Tourist(
        name=tourist.name,
        email=tourist.email,
        phone=tourist.phone,
        password_hash=hashed_password,
        emergency_contact=tourist.emergency_contact
    )

    db.add(new_tourist)
    db.commit()
    db.refresh(new_tourist)

    return {
        "message": "Tourist registered successfully",
        "tourist_id": new_tourist.tourist_id,
        "name": new_tourist.name,
        "email": new_tourist.email
    }


@app.post("/login")
def login_tourist(
    tourist: TouristLogin,
    db: Session = Depends(get_db)
):
    existing_tourist = (
        db.query(models.Tourist)
        .filter(models.Tourist.email == tourist.email)
        .first()
    )

    if not existing_tourist:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        tourist.password,
        existing_tourist.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "tourist_id": existing_tourist.tourist_id,
        "name": existing_tourist.name,
        "email": existing_tourist.email
    }
@app.get("/zones")
def get_zones(db: Session = Depends(get_db)):
    zones = db.query(models.Zone).all()

    return [
        {
            "zone_id": zone.zone_id,
            "zone_name": zone.zone_name,
            "zone_type": zone.zone_type,
            "latitude": float(zone.latitude),
            "longitude": float(zone.longitude),
            "radius": zone.radius,
            "risk_level": zone.risk_level,
            "description": zone.description
        }
        for zone in zones
    ]
@app.post("/sos")
def create_sos_alert(
    tourist_id: int,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    new_alert = models.Alert(
        tourist_id=tourist_id,
        alert_type="SOS",
        risk_level="CRITICAL",
        latitude=str(latitude),
        longitude=str(longitude),
        message="Emergency SOS activated",
        status="ACTIVE"
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return {
        "message": "SOS alert created successfully",
        "alert_id": new_alert.alert_id,
        "tourist_id": new_alert.tourist_id,
        "risk_level": new_alert.risk_level
    }
@app.post("/zone-alert")
def create_zone_alert(
    tourist_id: int,
    latitude: float,
    longitude: float,
    alert_type: str,
    risk_level: str,
    message: str,
    db: Session = Depends(get_db)
):
    new_alert = models.Alert(
        tourist_id=tourist_id,
        alert_type=alert_type,
        risk_level=risk_level,
        latitude=str(latitude),
        longitude=str(longitude),
        message=message,
        status="ACTIVE"
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return {
        "message": "Zone alert created successfully",
        "alert_id": new_alert.alert_id,
        "tourist_id": tourist_id,
        "alert_type": alert_type,
        "risk_level": risk_level
    }
@app.post("/calculate-risk")
def calculate_tourist_risk(
    zone_risk: str,
    speed: float,
    stationary_time: float,
    route_deviation: bool,
    night_movement: bool
):
    result = calculate_risk(
        zone_risk,
        speed,
        stationary_time,
        route_deviation,
        night_movement
    )

    return result
