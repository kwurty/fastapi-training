from .. import utils, models, schemas, oath2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
import re

# create router object
router = APIRouter(
    prefix="/users",
    # below is for the Swagger UI (http://localhost:8000/docs) to categorize based on the tag
    tags=['Users']
)


@router.get('/followexample')
def follow_example(user: int = Depends(oath2.get_current_user), db: Session= Depends(get_db)):
    following = db.query(func.count(models.Follow.user_id).label("following")).filter(models.Follow.user_id == user.id).all()
    return following

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOutToken)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Reference the create post for info. This is the same

    if not db.query(models.User).filter(models.User.email == user.email.lower()).first():
        if not db.query(models.User).filter(models.User.username == user.username.lower()).first():
            # Create hash of password
            hashed_password = utils.hashPassword(user.password)
            user.password = hashed_password
            user.email = user.email.lower()
            user.username = re.sub(r"\s+", "", user.username.lower(), flags=re.UNICODE)
            new_user = models.User(**user.dict())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            token = oath2.create_access_token(
                data={"user_id": new_user.id, "username": new_user.username})
            new_user.access_token = token
            new_user.token_type = "Bearer"
            return new_user
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Account with username {user.username} already exists")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Account with email {user.email} already exists")


# @router.get("/follow", status_code=status.HTTP_200_OK, response_model=schemas.Follow)
# def get_followers(db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):

#     followers = db.query(models.Follow).filter(
#         models.Follow.user_id == current_user.id).all()
#     if not followers:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"User id {id} not found with followers")
#     else:
#         return followers


@router.get('/follow', status_code=status.HTTP_200_OK)
async def get_followers(db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    followers = db.query(models.Follow).filter(
        models.Follow.user_id == current_user.id
    ).all()

    return followers


@router.post("/follow/{id}", status_code=status.HTTP_201_CREATED)
async def follow_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):

    followers_query = db.query(models.Follow).filter(
        models.Follow.user_id == current_user.id, models.Follow.follow_user_id == id)
    follower_found = followers_query.first()

    if(follower_found):
        followers_query.delete(synchronize_session=False)
        db.commit()
        return {"follow_user" : id, "following" : False}

    else:
        new_follow = models.Follow(user_id=current_user.id, follow_user_id=id)
        db.add(new_follow)
        db.commit()
        return {"follow_user" : id, "following" : True}
        

@router.get('/explore', )
def get_random_users(db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    
    followed_users = db.query(models.Follow.follow_user_id).filter(models.Follow.user_id == current_user.id).group_by(models.Follow.follow_user_id).subquery()
    
    users = db.query(models.User, followed_users.c.follow_user_id).join(followed_users, models.User.id == followed_users.c.follow_user_id, isouter=True).order_by(func.random()).limit(10).all()

    return users

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOutFollowers)
def get_user(id: str, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    user = db.query(models.User).filter(models.User.username == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with username {id} was not found")

    following = db.query(models.Follow.user_id, func.count(models.Follow.user_id).label("following")).filter(models.Follow.user_id == user.id).group_by(models.Follow.user_id).all()
    followers = db.query(models.Follow.follow_user_id, func.count(models.Follow.user_id).label("followed")).filter(models.Follow.follow_user_id == user.id).group_by(models.Follow.follow_user_id).all()
    isfollowing = db.query(models.Follow.user_id).filter(models.Follow.follow_user_id == user.id, models.Follow.user_id == current_user.id).first()

    if(isfollowing == None):
        user.is_following = False
    else:
        user.is_following = True

    if (len(followers)> 0) :
        user.followers = followers[0][1]
    else:
        user.followers = 0
    if  (len(following) > 0):
        user.following = following[0][1]
    else:
        user.following = 0
        
    return user


# Do the actual update
@router.put('/{id}', response_model=schemas.UserOut)
def update_user(id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):

    if( id != current_user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"You are not authorized to edit user with id {id}")
    
    updated_user = db.query(models.User).filter(models.User.id == id).first()

    for attr, val in user:
        if(val != None):
            setattr(updated_user, attr, val)

    db.commit()
    return updated_user

@router.get('/{id}/posts', response_model=List[schemas.PostOut])
def get_users_posts(id: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 50,  current_user: int = Depends(oath2.get_current_user) ):

    user = db.query(models.User).filter(models.User.username == id).first()
    if (not user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {id} not found")

    liked_post = (db.query(models.Vote.post_id.label("post_id"), func.count(models.Vote.user_id).label("liked_post")).filter(models.Vote.user_id == current_user.id).group_by(models.Vote.post_id).subquery())
        

    posts = (db.query(models.Post, func.count(models.Vote.post_id).label("votes"), liked_post.c.liked_post)\
                .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
                    .outerjoin(liked_post, models.Post.id == liked_post.c.post_id)\
                        .group_by(models.Post.id, liked_post.c.liked_post)\
                            .filter(models.Post.user_id == user.id)\
                                .limit(limit)\
                                    .offset(skip)\
                                        .all())

    return posts


# Return the info for the logged in user  
@router.get('/',  response_model=schemas.UserProfile)
def get_logged_in_user(db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if not (user):
        raise HTTPException(stauts_code=status.HTTP_404_NOT_FOUND, detail=f"You are not authorized to view user")
    return user

