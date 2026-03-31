import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import (
    create_access_token,
    get_db,
    hash_password,
    verify_password,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/signup")
def signup(payload: schemas.UserSignup, db: Session = Depends(get_db)):
    try:
        existing_user = (
            db.query(models.User).filter(models.User.email == payload.email).first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = models.User(email=payload.email, password=hash_password(payload.password))
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"id": user.id, "email": user.email}
    except HTTPException:
        raise
    except IntegrityError as exc:
        db.rollback()
        logger.exception("Signup failed due to database integrity error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected signup error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user at this time",
        )


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(access_token=access_token)
