from sqlalchemy.orm import Session
from . import models


def create_lead(db: Session, lead):
    db_lead = models.Lead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def get_leads(db):
    return db.query(models.Lead).all()


def create_property(db: Session, prop):
    db_prop = models.Property(**prop.dict())
    db.add(db_prop)
    db.commit()
    db.refresh(db_prop)
    return db_prop