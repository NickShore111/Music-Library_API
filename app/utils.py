from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from . import models
from sqlalchemy.orm import Session
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
