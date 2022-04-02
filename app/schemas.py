from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint

# Use Pydantic to define the posts schema
# Refer to BaseModel


class Follow(BaseModel):
    user_id: str
    follow_user_id: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    displayname: str
    email: EmailStr
    created_at: datetime


    class Config:
        orm_mode = True

class UserOutFollowers(UserOut):
    followers: int
    following: int    
    class Config:
        orm_mode = True

class UserOutToken(BaseModel):
    id: int
    username: str
    displayname: str
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

class UserProfile(BaseModel):
    id: int
    username: str
    displayname: str
    email: EmailStr
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[str]
    displayname: Optional[str]
    email: Optional[EmailStr]
    

class TokenData(BaseModel):
    id: Optional[str]
    username: str
    displayname: str


class PostBase(BaseModel):
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
    liked_post: Optional[int]

    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id: int
    dir: int

class Hashtag(BaseModel):
    hashtag: str
    count: int
    class Config:
        orm_mode = True

class HashtagNoCount(BaseModel):
    hashtag: str
    class Config:
        orm_mode = True