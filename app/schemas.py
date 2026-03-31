from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSignup(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LeadCreate(BaseModel):
    name: str
    phone: str
    follow_up_date: Optional[datetime] = None
    property_id: Optional[int] = None


class LeadResponse(BaseModel):
    id: int
    name: str
    phone: str
    status: str

    class Config:
        from_attributes = True


class PropertyCreate(BaseModel):
    location: str
    price: int
    type: str

class WhatsAppWebhook(BaseModel):
    name: str
    phone: str
