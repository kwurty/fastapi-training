from .. import utils, models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter

# create router object
router = APIRouter(
    prefix="/users",
    # below is for the Swagger UI (http://localhost:8000/docs) to categorize based on the tag
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Reference the create post for info. This is the same
    """
    hello! I can write crap in here I guess and it's a comment?
    """

    if not db.query(models.User).filter(models.User.email == user.email).first():

        # Create hash of password
        hashed_password = utils.hashPassword(user.password)
        user.password = hashed_password
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Account with email {user.email} already exists")


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} was not found")

    return user
