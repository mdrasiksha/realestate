from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    return crud.create_lead(db, lead)


@router.get("/")
def list_leads(db: Session = Depends(get_db)):
    return crud.get_leads(db)


@router.get("/today-followups")
def get_today_followups(db: Session = Depends(get_db)):
    today = date.today()
    return (
        db.query(models.Lead)
        .filter(
            models.Lead.follow_up_date.isnot(None),
            func.date(models.Lead.follow_up_date) == today,
        )
        .all()
    )
