from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint

# Use Pydantic to define the posts schema
# Refer to BaseModel


class Follow(BaseModel):
    user_id: int
    follow_user_id: int


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserOutToken(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    access_token: str
    token_type: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserToken(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]
    username: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    # This will convert the SQLAlchemy model to a dict that Pydantic can return
    # class Config:
    #     orm_mode = True


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


# Response model for a post. It will send back exactly what is placed below PLUS the inherited PostBase model
class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id: int
    dir: int
