from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_current_user, get_db
from .. import crud, models, schemas

router = APIRouter()


@router.post("/")
def create_property(
    prop: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_property(db, prop)
