from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..dependencies import get_current_user, get_db

router = APIRouter()


@router.post("/")
def create_lead(
    lead: schemas.LeadCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_lead(db, lead, current_user.id)


@router.get("/")
def list_leads(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_leads(db, current_user.id)


@router.get("/today-followups")
def get_today_followups(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = date.today()
    return (
        db.query(models.Lead)
        .filter(
            models.Lead.user_id == current_user.id,
            models.Lead.follow_up_date.isnot(None),
            func.date(models.Lead.follow_up_date) == today,
        )
        .all()
    )
