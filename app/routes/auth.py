from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, utils, oath2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])


@router.post('/login', response_model=schemas.UserToken)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username.lower()).first()

    # check if user exist in db
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")

    # generate token with login password and compare w/ token in database
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")

    # generate token
    token = oath2.create_access_token(
        data={"user_id": user.id, "username": user.username, "displayname": user.displayname})

    return {"access_token": token, "token_type": "bearer"}

@router.get('/refresh', response_model=schemas.UserToken)
def refresh_token(db: Session=Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    token = oath2.create_access_token(
        data={"user_id": user.id, "username": user.username, "displayname": user.displayname})
    
    return {"access_token": token, "token_type": "bearer"}