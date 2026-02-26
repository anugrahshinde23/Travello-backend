from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class Role(str, Enum) : 
    USER="user",
    ADMIN="admin"

class UserRegister(BaseModel) :
    name : str
    email : EmailStr
    password : str
    role : Role = Role.USER
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserLogin(BaseModel) : 
    email : EmailStr
    password : str 
