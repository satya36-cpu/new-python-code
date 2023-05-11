import pdb
import os
import rsa
from fastapi import APIRouter
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.users import  get_current_active_user, user_registrations, edit_user_registrations,verify
from app.schemas.users import User, UserInDB, UsersDB,UserEdit
from app.services.oauth2 import verify_access_token,create_access_token
from sqlalchemy.orm import Session
from core.config import engine, SessionLocal,get_db

user_app = APIRouter()


@user_app.post("/registration")
async def registration(data: UserInDB, db: Session = Depends(get_db)):
    try:
        response = user_registrations(db, data)
        return {"status": True, "result": response}
    except Exception as e:
        print(f"exceptions are {e}")
        return {"status": False, "result": "something went wrong"}


#
@user_app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    privateKey = eval(os.getenv('PASSWORD_PRIVATE_KEY'))
    privateKey = rsa.PrivateKey(privateKey[0], privateKey[1],privateKey[2],privateKey[3],privateKey[4])
    user_dict = db.query(UsersDB).filter(UsersDB.username == form_data.username,).first()
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    encMessage = rsa.decrypt(eval(user_dict.encrypted_password), privateKey).decode()
    if not form_data.password == encMessage:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user_dict.token, "token_type": "bearer"}


@user_app.post('/login')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(UsersDB).filter(
        UsersDB.email == user_credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not verify(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # create a token
    # return token

    access_token = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@user_app.get("/users/token")
async def read_users_me(current_user: UsersDB = Depends(get_current_active_user)):
    context ={
        "username":current_user.username,
        "token":current_user.token
    }
    return context

@user_app.get("/users/get")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    context ={
        # "username":current_user.username,
        # "id":current_user.id,
        "first_name":current_user.first_name,
        "last_name":current_user.last_name,
        # "roles": current_user.roles.tobytes(),
        "roles": current_user.roles,
        "phone":current_user.phone,
        "email":current_user.email,
        "is_active":current_user.is_active,
        "create_by":current_user.create_by,
        "create_date":current_user.create_date,
    }
    return context

@user_app.post("/users/edit")
async def read_users_me(data: UserEdit, current_user: UsersDB = Depends(get_current_active_user)):
    try:
        response = edit_user_registrations(data,current_user)
        return {"status": True, "result":response}
    except Exception as e:
        print(f"exceptions are {e}")
        return {"status": False, "result": "something went wrong"}
