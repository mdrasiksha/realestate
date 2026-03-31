from sqlalchemy.orm import Session
from . import models


def create_lead(db: Session, lead, user_id: int):
    db_lead = models.Lead(**lead.dict(), user_id=user_id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def get_leads(db: Session, user_id: int):
    return db.query(models.Lead).filter(models.Lead.user_id == user_id).all()


def create_property(db: Session, prop):
    db_prop = models.Property(**prop.dict())
    db.add(db_prop)
    db.commit()
    db.refresh(db_prop)
    return db_prop
