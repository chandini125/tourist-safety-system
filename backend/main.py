
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import Base, engine, SessionLocal
import models
from schemas import TouristCreate, TouristLogin
from auth import verify_password
from ai.risk_engine import calculate_risk
from blockchain.blockchain import Blockchain, create_identity_hash
import os
from fastapi.staticfiles import StaticFiles
app=FastAPI(title="Tourist Safety System")
STATIC_DIR = os.path.join(
    os.path.dirname(__file__),
    "static"
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

Base.metadata.create_all(bind=engine)
app=FastAPI(title="Tourist Safety System")

blockchain=Blockchain()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://10.53.116.242:5500"],
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
@app.get("/tourist-risk/{tourist_id}")
def get_tourist_risk(
    tourist_id: int,
    db: Session = Depends(get_db)
):
    latest_location = (
        db.query(models.Location)
        .filter(models.Location.tourist_id == tourist_id)
        .order_by(models.Location.location_id.desc())
        .first()
    )

    if not latest_location:
        raise HTTPException(
            status_code=404,
            detail="No location data found"
        )

    latest_alert = (
        db.query(models.Alert)
        .filter(models.Alert.tourist_id == tourist_id)
        .order_by(models.Alert.alert_id.desc())
        .first()
    )

    zone_risk = "LOW"

    if latest_alert:
        if latest_alert.risk_level in [
            "LOW", "MEDIUM", "HIGH", "CRITICAL"
        ]:
            zone_risk = latest_alert.risk_level

    speed = float(latest_location.speed or 0)

    night_movement = False

    if latest_location.timestamp:
        hour = latest_location.timestamp.hour
        night_movement = hour >= 22 or hour < 6

    result = calculate_risk(
        zone_risk=zone_risk,
        speed=speed,
        stationary_time=0,
        route_deviation=False,
        night_movement=night_movement
    )

    return {
        "tourist_id": tourist_id,
        "zone_risk": zone_risk,
        "speed": speed,
        "night_movement": night_movement,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"]
    }
@app.get("/blockchain")
def get_blockchain():
    return [
        {
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        }
        for block in blockchain.chain
    ]
@app.post("/digital-id/create/{tourist_id}")
def create_digital_id(
    tourist_id: int,
    db: Session = Depends(get_db)
):
    # Find the tourist
    tourist = (
        db.query(models.Tourist)
        .filter(models.Tourist.tourist_id == tourist_id)
        .first()
    )

    if not tourist:
        raise HTTPException(
            status_code=404,
            detail="Tourist not found"
        )

    # Check whether Digital ID already exists
    existing_id = (
        db.query(models.DigitalID)
        .filter(models.DigitalID.tourist_id == tourist_id)
        .first()
    )

    if existing_id:
        return {
            "message": "Digital ID already exists",
            "digital_id": existing_id.digital_id,
            "id_hash": existing_id.id_hash,
            "status": existing_id.status
        }

    # Generate Digital ID
    digital_id = f"ST-{tourist_id:06d}"

    # Create identity hash
    identity_hash = create_identity_hash(
        tourist.tourist_id,
        digital_id,
        tourist.name,
        tourist.email
    )

    # Add identity information to blockchain
    block = blockchain.add_block({
        "digital_id": digital_id,
        "tourist_id": tourist.tourist_id,
        "identity_hash": identity_hash,
        "purpose": "Digital Tourist ID verification"
    })

    # Save Digital ID
    new_digital_id = models.DigitalID(
        tourist_id=tourist.tourist_id,
        digital_id=digital_id,
        id_hash=identity_hash,
        status="ACTIVE"
    )

    db.add(new_digital_id)

    # Save blockchain record in MySQL
    blockchain_record = models.BlockchainRecord(
        digital_id=digital_id,
        transaction_hash=identity_hash,
        block_hash=block.hash
    )

    db.add(blockchain_record)

    db.commit()
    db.refresh(new_digital_id)

    return {
        "message": "Digital ID created and recorded on blockchain",
        "tourist_id": tourist.tourist_id,
        "digital_id": digital_id,
        "id_hash": identity_hash,
        "block_index": block.index,
        "block_hash": block.hash,
        "previous_hash": block.previous_hash,
        "status": "ACTIVE"
    }
@app.get("/digital-id/verify/{digital_id}")
def verify_digital_id(
    digital_id: str,
    db: Session = Depends(get_db)
):
    digital_record = (
        db.query(models.DigitalID)
        .filter(models.DigitalID.digital_id == digital_id)
        .first()
    )

    if not digital_record:
        raise HTTPException(
            status_code=404,
            detail="Digital ID not found"
        )

    tourist = (
        db.query(models.Tourist)
        .filter(
            models.Tourist.tourist_id
            == digital_record.tourist_id
        )
        .first()
    )

    if not tourist:
        raise HTTPException(
            status_code=404,
            detail="Tourist not found"
        )

    # Recalculate the identity hash
    current_hash = create_identity_hash(
        tourist.tourist_id,
        digital_record.digital_id,
        tourist.name,
        tourist.email
    )

    # Compare with the original stored hash
    if current_hash == digital_record.id_hash:
        verification_status = "VALID"
    else:
        verification_status = "INVALID"

    return {
        "digital_id": digital_record.digital_id,
        "tourist_id": tourist.tourist_id,
        "tourist_name": tourist.name,
        "tourist_email": tourist.email,
        "verification_status": verification_status,
        "stored_hash": digital_record.id_hash,
        "current_hash": current_hash
    }
import qrcode
import os
@app.get("/digital-id/qr/{digital_id}")
def generate_digital_id_qr(
    digital_id: str,
    db: Session = Depends(get_db)
):
    digital_record = (
        db.query(models.DigitalID)
        .filter(models.DigitalID.digital_id == digital_id)
        .first()
    )

    if not digital_record:
        raise HTTPException(
            status_code=404,
            detail="Digital ID not found"
        )

    qr_data = (
        f"http://127.0.0.1:8000/"
        f"digital-id/verify/{digital_id}"
    )

    qr = qrcode.make(qr_data)

    qr_folder = os.path.join(os.path.dirname(__file__),"static","qr")
    os.makedirs(qr_folder, exist_ok=True)

    qr_path = f"{qr_folder}/{digital_id}.png"
    qr.save(qr_path)

    return {
        "message": "QR code generated successfully",
        "digital_id": digital_id,
        "qr_file": qr_path,
        "verification_url": qr_data
    }
@app.post("/locations")
def save_location(
    tourist_id: int,
    latitude: float,
    longitude: float,
    speed: float = 0,
    db: Session = Depends(get_db)
):
    new_location = models.Location(
        tourist_id=tourist_id,
        latitude=str(latitude),
        longitude=str(longitude),
        speed=str(speed)
    )

    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return {
        "message": "Location saved successfully",
        "location_id": new_location.location_id,
        "tourist_id": new_location.tourist_id,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed
    }
@app.get("/locations/{tourist_id}")
def get_locations(
    tourist_id: int,
    db: Session = Depends(get_db)
):
    locations = (
        db.query(models.Location)
        .filter(models.Location.tourist_id == tourist_id)
        .order_by(models.Location.location_id.desc())
        .all()
    )

    return [
        {
            "location_id": location.location_id,
            "tourist_id": location.tourist_id,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "speed": float(location.speed or 0),
            "timestamp": location.timestamp
        }
        for location in locations
    ]
@app.get("/alerts/{tourist_id}")
def get_tourist_alerts(
    tourist_id: int,
    db: Session = Depends(get_db)
):
    alerts = (
        db.query(models.Alert)
        .filter(models.Alert.tourist_id == tourist_id)
        .order_by(models.Alert.alert_id.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type,
            "risk_level": alert.risk_level,
            "message": alert.message,
            "status": alert.status,
            "created_at": alert.created_at
        }
        for alert in alerts
    ]
@app.get("/tourists")
def get_tourists(db: Session = Depends(get_db)):
    tourists = (
        db.query(models.Tourist)
        .order_by(models.Tourist.tourist_id.asc())
        .all()
    )

    return [
        {
            "tourist_id": tourist.tourist_id,
            "name": tourist.name,
            "email": tourist.email,
            "created_at": tourist.created_at
        }
        for tourist in tourists
    ]
