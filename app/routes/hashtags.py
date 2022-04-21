
from fastapi import APIRouter

from fastapi import status, HTTPException, Depends, APIRouter
from datetime import datetime, timedelta
from sqlalchemy import desc, func, distinct
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oath2
from ..database import get_db

# create router object
router = APIRouter(
    prefix="/hashtags",
    # below is for the Swagger UI (http://localhost:8000/docs) to categorize based on the tag
    tags=['Hashtags']
)



@router.get('/latest', response_model=List[schemas.HashtagNoCount])
def get_latest_hashtags(db: Session=Depends(get_db)):
    thirty_days_ago = datetime.now() - timedelta(days=30) 
   
    hashtags = db.query(models.Hashtag.hashtag.distinct().label("hashtag")).filter(models.Hashtag.created_at > thirty_days_ago).limit(30).all()
    return hashtags

@router.get('/explore', response_model=List[schemas.HashtagNoCount])
def get_latest_hashtags(db: Session=Depends(get_db)):
    distinct_hashtags = db.query(models.Hashtag.hashtag.distinct().label("hashtag")).subquery()
    hashtags = db.query(distinct_hashtags).order_by(func.random()).limit(10).all()
    return hashtags

@router.get('/', response_model=List[schemas.Hashtag])
def get_hashtags(db: Session = Depends(get_db)):

    thirty_days_ago = datetime.now() - timedelta(days=30) 
    hashtags = db.query(models.Hashtag.hashtag, func.count(models.Hashtag.hashtag).label("count")).filter(models.Hashtag.created_at >= thirty_days_ago).group_by(models.Hashtag.hashtag).order_by(desc("count")).all()
    return hashtags