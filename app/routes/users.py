from .. import utils, models, schemas, oath2
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter

# create router object
router = APIRouter(
    prefix="/users",
    # below is for the Swagger UI (http://localhost:8000/docs) to categorize based on the tag
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOutToken)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Reference the create post for info. This is the same
    """
    hello! I can write crap in here I guess and it's a comment?
    """

    if not db.query(models.User).filter(models.User.email == user.email.lower()).first():
        if not db.query(models.User).filter(models.User.username == user.username.lower()).first():
            # Create hash of password
            hashed_password = utils.hashPassword(user.password)
            user.password = hashed_password
            user.email = user.email.lower()
            user.username = user.username.lower()
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
        return {"message", "Successfully unfollowed user with id {id}"}

    else:
        new_follow = models.Follow(user_id=current_user.id, follow_user_id=id)
        db.add(new_follow)
        db.commit()
        return {"message", "Successfully followed user with id {id}"}


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} was not found")

    return user
