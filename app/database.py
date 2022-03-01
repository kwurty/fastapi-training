from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db

    # close out connection when we're done
    finally:
        db.close()


#  Below is the code that was in Main.py. It connected to the database before we implemented SQLAlchemy. This is used for direct connection and querying of the database
# Get session to Database
# while True:
#     try:
#         conn = psycopg2.connect(host='', database='',
#                                 user='', password='', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connected")
#         break

#     except Exception as error:
#         print("Connection to database failed")
#         print("Error: ", error)
#         time.sleep(2)
