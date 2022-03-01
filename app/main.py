# Optional type checking
# from psycopg2.extras import RealDictCursor
# import psycopg2

# import sleep module
# import time

# Import models from the models file in current directory
# from . import models, schemas, utils
from .routes import users, posts, auth, vote
from .config import settings
from . import models


# Import the engine and db connection from our database
from .database import get_db, engine

# # Import the ORM Items. Currently using SQLAlchemy for that functionality
# from sqlalchemy.orm import Session

# Import the main framework (FastAPI)
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]


# Allows gathering from posts' body
# from fastapi.params import Body

# Import pydantic to create schemas
# from pydantic import BaseModel

# Import random number support --- sHIT there's a lot of importing in Python
# from random import randrange


# Import the SQL items. This is to use it WITHOUT the

# Basically this is grabbing the Base models from the models.py file
# and then creating the table for each model.
# It is "binding" to the engine which was created in our database file.

# We turned this off because we are using Alembic
# models.Base.metadata.create_all(bind=engine)

# Declare the app (same as Express)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Temporary array for posts
# my_posts = [{"title": "Post 1 post", "content": "content of post 1", "id": 1},
#             {"title": "Chicken", "content": "Tendieeesss", "id": 2}]


# Temporary hunt for correct ID
# def find_post(id):
#     for p in my_posts:
#         if p["id"] == id:
#             return p


# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if p['id'] == id:
#             return i

# Create the routes (probably some sort of router we can use later, but for now this is where we're at)


app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root():

    return {"message": "Hello World"}

# Just routing, pretty basic stuff
