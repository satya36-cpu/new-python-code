import datetime
from typing import Union
from typing import List, Optional
from datetime import date, datetime
import rsa
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from pydantic import BaseModel, NonNegativeInt, EmailStr
from pydantic.types import constr
from core.config import Base, engine
from sqlalchemy import Boolean, DateTime, Column, ForeignKey, Integer, String, ARRAY, JSON,False_

from pydantic import BaseModel


class Common(BaseModel):
    email: EmailStr
    first_name: constr(strip_whitespace=True)
    last_name: constr(strip_whitespace=True)
    phone: constr(strip_whitespace=True)
    is_active: bool
    roles: List[constr(strip_whitespace=True)]


class User(Common):
    create_date: datetime
    create_by:Optional[int]


class UserInDB(User):
    password: str


class UserEdit(Common):
    pass

class TokenData(BaseModel):
    id: Optional[str] = None


class UsersDB(Base):
    __tablename__ = "users"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(String, index=True, primary_key=True,nullable=False)
    username = Column(String, index=True,unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    roles = Column(JSON)
    hashed_password = Column(String)
    create_date = DateTime()
    create_by = Column(String,default=None)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "is_active": self.is_active,
            "roles": self.roles,
            "create_date": self.create_date,
            "create_by": self.create_by,
        }

    def get_token(self):
        return {
            "token": self.token,
        }

    def get_password(self):
        return {
            "encrypted_password": self.hashed_password,
        }


Base.metadata.create_all(engine)
