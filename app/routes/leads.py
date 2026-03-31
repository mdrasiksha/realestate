from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=schemas.LeadRead)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    return crud.create_lead(db, lead)


@router.get("/", response_model=list[schemas.LeadRead])
def get_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_leads(db, skip=skip, limit=limit)
