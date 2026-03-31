from sqlalchemy.orm import Session

from . import models, schemas


def create_lead(db: Session, lead: schemas.LeadCreate) -> models.Lead:
    db_lead = models.Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def list_leads(db: Session, skip: int = 0, limit: int = 100) -> list[models.Lead]:
    return db.query(models.Lead).offset(skip).limit(limit).all()


def create_property(db: Session, property_in: schemas.PropertyCreate) -> models.Property:
    db_property = models.Property(**property_in.model_dump())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


def list_properties(db: Session, skip: int = 0, limit: int = 100) -> list[models.Property]:
    return db.query(models.Property).offset(skip).limit(limit).all()
