from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import Base, engine, SessionLocal
import models
from schemas import TouristCreate, TouristLogin
from auth import verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tourist Safety System")

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