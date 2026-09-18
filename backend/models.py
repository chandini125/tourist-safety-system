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