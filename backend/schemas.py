from pydantic import BaseModel, EmailStr


class TouristCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    password: str
    emergency_contact: str | None = None

class TouristLogin(BaseModel):
    email:EmailStr
    password: str