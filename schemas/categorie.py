import base64
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategorieBase(BaseModel):
    name           : str
    description    : Optional[str] = None
    icon           : Optional[str] = None

class CategorieCreate(CategorieBase):
    pass

class LinkLocal(BaseModel):
    local_id: int

class CategorieSync(BaseModel):


    sync_id     : Optional[int] = None

    server_id       : Optional[int] = None
    
    name        : str
    description : Optional[str] = None
    icon        : Optional[str] = None

    deleted     : int = 0

    created_at  : Optional[datetime] = None
    update_at   : Optional[datetime] = None


class CategorieUpdate(BaseModel):
    name           : Optional[str] = None
    description    : Optional[str] = None
    icon           : Optional[str] = None


class CategorieResponse(CategorieBase):
    id              : int
    name            : str
    description     : Optional[str] = None
    icon            : Optional[str] = None
    synced          : int
    sync_id         : int
    deleted         : int


    created_at  : datetime
    update_at   : datetime

    class Config:
        
        from_attributes = True
