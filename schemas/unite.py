from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UniteBase(BaseModel):
    niveau_1 : Optional[str] = None
    niveau_2 : Optional[str] = None
    niveau_3 : Optional[str] = None

class UniteCreate(UniteBase):
    pass

class UniteSync(BaseModel):

    sync_id     : Optional[int] = None

    server_id       : Optional[int] = None

    niveau_1 : Optional[str] = None
    niveau_2 : Optional[str] = None
    niveau_3 : Optional[str] = None

    deleted     : int = 0

    created_at  : Optional[datetime] = None
    update_at   : Optional[datetime] = None


class UniteUpdate(BaseModel):
    niveau_1 : Optional[str] = None
    niveau_2 : Optional[str] = None
    niveau_3 : Optional[str] = None

class UniteResponse(UniteBase):
    id         : int
    synced     : int
    sync_id    : int
    deleted    : int
    update_at  : datetime
    created_at : datetime
    class Config:
        from_attributes = True
