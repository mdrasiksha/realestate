from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/properties", tags=["properties"])


@router.post("/", response_model=schemas.PropertyRead)
def create_property(property_in: schemas.PropertyCreate, db: Session = Depends(get_db)):
    return crud.create_property(db, property_in)


@router.get("/", response_model=list[schemas.PropertyRead])
def get_properties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_properties(db, skip=skip, limit=limit)
