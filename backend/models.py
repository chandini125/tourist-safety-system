from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func

from database import Base


class Tourist(Base):
    __tablename__ = "tourists"

    tourist_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(15))
    password_hash = Column(String(255))
    emergency_contact = Column(String(15))
    created_at = Column(TIMESTAMP, server_default=func.now())
class Zone(Base):
    __tablename__ = "zones"

    zone_id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(100), nullable=False)
    zone_type = Column(String(30), nullable=False)
    latitude = Column(String(20), nullable=False)
    longitude = Column(String(20), nullable=False)
    radius = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    description = Column(String(255))
class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, index=True)
    tourist_id = Column(Integer, nullable=False)
    alert_type = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False)
    latitude = Column(String(20))
    longitude = Column(String(20))
    message = Column(String(255))
    status = Column(String(20), default="ACTIVE")
    created_at = Column(TIMESTAMP, server_default=func.now())
