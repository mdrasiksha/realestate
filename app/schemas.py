from datetime import datetime

from pydantic import BaseModel, EmailStr


class LeadBase(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    status: str = "new"


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class PropertyBase(BaseModel):
    title: str
    city: str
    price: float


class PropertyCreate(PropertyBase):
    pass


class PropertyRead(PropertyBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class WebhookPayload(BaseModel):
    source: str
    event: str
    message: str | None = None
