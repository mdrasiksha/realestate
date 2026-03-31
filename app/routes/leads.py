from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas, models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    new_lead = models.Lead(
        name=lead.name,
        phone=lead.phone,
        follow_up_date=lead.follow_up_date,
        property_id=lead.property_id
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead

@router.get("/")
def list_leads(db: Session = Depends(get_db)):
    return crud.get_leads(db)



"""from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test_leads():
    return {"message": "leads working"}"""



#from fastapi import APIRouter

#router = APIRouter()

#@router.get("/")
#def test_properties():
#    return {"message": "properties working"}




