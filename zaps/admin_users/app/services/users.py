import time
from datetime import datetime
import os
import pdb
import uuid
from sqlalchemy import exc
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from app.schemas.users import User, UserInDB, UsersDB, UserEdit
from app.services.oauth2 import get_current_user
from sqlalchemy.orm import Session
from core.config import SessionLocal
from sqlalchemy.sql.expression import false
import rsa

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     db = SessionLocal()
#     user = db.query(UsersDB).filter(UsersDB.id == token).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def new_user_id(db):
    while True:
        id = str(uuid.uuid4())
        data = db.query(UsersDB).filter(
            UsersDB.id == id).first()
        if not data:
            return id


def user_registrations(db: Session, user: UserInDB):
    try:
        hashed_password = hash(user.password)
        id = new_user_id(db)
        db_user = UsersDB(
            id=id,
            email=user.email,
            username=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            is_active=True,
            roles=user.roles,
            hashed_password=hashed_password,
            create_date=datetime.utcnow(),
            create_by=user.create_by,

        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user.to_dict()
    except exc.IntegrityError as e:
        print(e)
        return "User Exist"
    except Exception as e:
        print(e)
        return "something went wrong"


def edit_user_registrations(user: UserEdit, current_user):
    try:
        db = SessionLocal()
        username = current_user.username

        current_user.first_name = user.first_name
        current_user.last_name = user.last_name
        current_user.phone = user.phone
        current_user.roles = user.roles
        current_user.is_active = user.is_active

        db.add(current_user)
        db.commit()
        return f"users {username} updated successfully"
    except exc.IntegrityError as e:
        print(e)
        return "User Exist"
    except Exception as e:
        print(e)
        return "something went wrong"
