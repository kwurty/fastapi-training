from cgitb import text
from datetime import datetime, timedelta
from itertools import count
import re
from .. import models, schemas, oath2
from ..database import get_db
from sqlalchemy import desc, func
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter
from better_profanity import profanity

# create router object
router = APIRouter(
    prefix="/posts",
    # below is for the Swagger UI (http://localhost:8000/docs) to categorize based on the tag
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.PostOut])
####
####
# Here you can see the query parameters in use
async def get_posts(db: Session = Depends(get_db), user_id: int = Depends(oath2.get_current_user), limit: int = 30, skip: int = 0, hashtag: Optional[str] = "", search: Optional[str] = ""):
    # This is for using actual SQL instead of using the ORM
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()

    if(len(hashtag) > 0):
        posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
            .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
                .join(models.Hashtag, models.Hashtag.post_id == models.Post.id, isouter=True)\
                    .filter(models.Hashtag.hashtag == hashtag)\
                        .group_by(models.Post.id)\
                            .order_by(desc(models.Post.created_at))\
                                .limit(limit)\
                                    .offset(skip)\
                                        .all()

    else: 
        liked_post = (db.query(models.Vote.post_id.label("post_id"), func.count(models.Vote.user_id).label("liked_post")).filter(models.Vote.user_id == user_id.id).group_by(models.Vote.post_id).subquery())
        

        posts = (db.query(models.Post, func.count(models.Vote.post_id).label("votes"), liked_post.c.liked_post)\
                    .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
                        .outerjoin(liked_post, models.Post.id == liked_post.c.post_id)\
                            .group_by(models.Post.id, liked_post.c.liked_post)\
                                .filter(models.Post.content.contains(search))\
                                    .limit(limit)\
                                        .offset(skip)\
                                            .all())
    return posts


@ router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
# Notice the use of the Class defined with Pydantic
# This will gather ONLY the items defined in the schema
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):

    # Generate the new post using the post schema
    # ** in this situation is like the ... in JS where it will deconstruct the object

    new_post = models.Post(user_id=current_user.id, **post.dict())
    new_post.content = profanity.censor(new_post.content)
    # queue the new post addition to the database
    db.add(new_post)

    # commit the new post to the database
    db.commit()

    # # retrieve the new_post info
    db.refresh(new_post)

    hashtags = re.findall(r"#(\w+)", new_post.content)
    hashtags = set(hashtags)

    for hashtag in hashtags:
        new_hashtag = models.Hashtag(user_id=current_user.id, post_id=new_post.id, hashtag=hashtag.lower())
        db.add(new_hashtag)
        db.commit()

# OLD SQL CODE - NOT ORM
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    return new_post

@router.get('/explore', response_model=List[schemas.PostOut])
def get_random_users(db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    # posts = db.query(models.Post).filter(models.Post.user_id != current_user.id).order_by(func.random()).limit(10).all()
    liked_post = (db.query(models.Vote.post_id.label("post_id"), func.count(models.Vote.user_id).label("liked_post")).filter(models.Vote.user_id == current_user.id).group_by(models.Vote.post_id).subquery())
        

    posts = (db.query(models.Post, func.count(models.Vote.post_id).label("votes"), liked_post.c.liked_post)\
                .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
                    .outerjoin(liked_post, models.Post.id == liked_post.c.post_id)\
                        .group_by(models.Post.id, liked_post.c.liked_post)\
                            .order_by(func.random())\
                                .limit(10)\
                                    .all())
    return posts


@router.get('/liked')
def get_liked_posts(current_user: int = Depends(oath2.get_current_user), db: Session = Depends(get_db)):
    liked_posts = db.query(models.Vote.post_id.label("post_id"), func.count(models.Vote.user_id).label("liked_post")).select_from(models.Vote)\
            .group_by(models.Vote.post_id)\
                .filter(models.Vote.user_id == current_user.id)\
                    .all()
    return liked_posts

@router.get('/hashtags', response_model=List[schemas.Hashtag])
def get_hashtags(db: Session = Depends(get_db)):

    thirty_days_ago = datetime.now() - timedelta(days=30) 
    hashtags = db.query(models.Hashtag.hashtag, func.count(models.Hashtag.hashtag).label("count")).filter(models.Hashtag.created_at >= thirty_days_ago).group_by(models.Hashtag.hashtag).order_by(desc("count")).all()
    return hashtags

@router.get('/hashtags/latest', response_model=List[schemas.HashtagNoCount])
def get_latest_hashtags(db: Session=Depends(get_db)):
    thirty_days_ago = datetime.now() - timedelta(days=30) 
    hashtags = db.query(models.Hashtag.hashtag.distinct().label("hashtag")).filter(models.Hashtag.created_at > thirty_days_ago).limit(30).all()
    return hashtags

@router.get('/hashtags/explore', response_model=List[schemas.HashtagNoCount])
def get_latest_hashtags(db: Session=Depends(get_db)):
    thirty_days_ago = datetime.now() - timedelta(days=30) 
    hashtags = db.query(models.Hashtag).order_by(func.random()).limit(10).all()
    return hashtags



@ router.get('/{id}', response_model=schemas.PostOut)
# id:int - will automatically convert the item to an integer. If a string cannot be changed, it will return error
# response - Will allow the response status to be changed (500, 404, etc.)
async def get_post(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oath2.get_current_user)):

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == str(id)).first()
    # post = db.query(models.Post).filter(models.Post.id == str(id)).first()

# PLAIN SQL CODE
    # cursor.execute(""" SELECT * FROM posts WHERE id=%s """, (str(id)))
    # post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return post



@ router.delete('/{id}')
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == str(id))

    if not post.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Post with id {id} not found")

    if post.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    # SQL ONLY - NO ORM
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", str(id))
    # post = cursor.fetchone()
    # conn.commit()


@router.put('/{id}', response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: dict = Depends(oath2.get_current_user)):
    # cursor.execute(
    #     """ UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # post = cursor.fetchone()
    # conn.commit()

    updated_post = db.query(models.Post).filter(models.Post.id == id)

    if not updated_post.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Post with id {id} not found")

    if updated_post.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    updated_post.update(post.dict(), synchronize_session=False)
    db.commit()
    return updated_post.first()


