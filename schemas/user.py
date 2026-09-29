from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from backend.models import user

# ----- Schéma de la base -----
class UserBase(BaseModel):

    name                : str
    first_name          : str
    middle_name         : str
    genre               : Optional[str] = None
    email               : EmailStr
    role                : str 


class UserCreate(UserBase):

    password            : str

class UserLogin(BaseModel):

    email               : str

    password            : str

class UserSync(BaseModel):

    sync_id             : Optional[int] = None

    server_id       : Optional[int] = None

    name        : str
    first_name  : str
    middle_name : str
    genre       : str | None
    email       : EmailStr
    role        : str
    password    : str   

    deleted             : int = 0

    created_at          : Optional[datetime] = None
    update_at           : Optional[datetime] = None


class UserUpdate(BaseModel) :

    name                : Optional[str] = None
    first_name          : Optional[str] = None
    middle_name         : Optional[str] = None
    genre               : Optional[str] = None
    email               : Optional[str] = None
    role                : Optional[str] = None 

class PasswordUpdate(BaseModel):
    
    new_password: str

class UserResponse(UserBase):

    id         : int
    synced     : int
    sync_id    : int
    deleted    : int


    created_at : datetime
    update_at  : datetime

    class Config:
        
        from_attributes = True


class Token(BaseModel):
    
    access_token        : str
    token_type          : str
    user                : UserResponse