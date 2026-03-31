from fastapi import APIRouter, Request
from ..database import SessionLocal
from .. import models

router = APIRouter()

from .. import schemas

@router.post("/whatsapp")
def whatsapp_webhook(payload: schemas.WhatsAppWebhook):
    db = SessionLocal()

    new_lead = models.Lead(
        name=payload.name,
        phone=payload.phone
    )

    db.add(new_lead)
    db.commit()
    db.close()

    return {"message": "Lead captured from WhatsApp"}