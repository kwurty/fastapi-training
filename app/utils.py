"""
    HASHING PASSWORDS IMPORTS
"""
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash password
def hashPassword(password: str):
    return pwd_context.hash(password)


def verify(pt_password, hashed_password):
    return pwd_context.verify(pt_password, hashed_password)
