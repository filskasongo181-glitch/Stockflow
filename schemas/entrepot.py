# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime


# class EntrepotBase(BaseModel):
#     reference     : str
#     description   : Optional[str] = None
#     localisation  : Optional[str] = None
#     capacity      : Optional[int] = None


# class EntrepotCreate(EntrepotBase):
#     pass

# class EntrepotSync(BaseModel):

#     sync_id         : Optional[int] = None

#     server_id       : Optional[int] = None

#     reference       : str
#     description     : Optional[str] = None
#     localisation    : Optional[str] = None
#     capacity        : Optional[int] = None

#     deleted         : int = 0

#     created_at      : Optional[datetime] = None
#     update_at       : Optional[datetime] = None


# class EntrepotUpdate(BaseModel):
#     reference     : Optional[str] = None
#     description   : Optional[str] = None
#     localisation  : Optional[str] = None
#     capacity      : Optional[int] = None


# class EntrepotResponse(EntrepotBase):
#     id            : int
#     reference     : Optional[str] = None
#     description   : Optional[str] = None
#     localisation  : Optional[str] = None
#     capacity      : Optional[int] = None
#     synced        : int
#     sync_id       : int
#     deleted       : int


#     created_at    : datetime
#     update_at     : datetime

#     class Config:
        
#         from_attributes = True



"""
schemas/entrepot.py
Convention SyncManager :
  payload.sync_id   = id LOCAL  → Server.sync_id
  payload.server_id = id MySQL  → lookup si déjà lié
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EntrepotBase(BaseModel):
    reference: str
    description: Optional[str] = None
    localisation: Optional[str] = None
    capacity: Optional[int] = None


class EntrepotCreate(EntrepotBase):
    pass


class EntrepotSync(BaseModel):
    """Payload push local → serveur (SyncManager._push_ids)."""
    sync_id: Optional[int] = None      # id LOCAL
    server_id: Optional[int] = None    # id MySQL (0 si nouveau)
    reference: str
    description: Optional[str] = None
    localisation: Optional[str] = None
    capacity: Optional[int] = None
    deleted: int = 0
    created_at: Optional[datetime] = None
    update_at: Optional[datetime] = None


class EntrepotUpdate(BaseModel):
    reference: Optional[str] = None
    description: Optional[str] = None
    localisation: Optional[str] = None
    capacity: Optional[int] = None


class EntrepotResponse(EntrepotBase):
    id: int
    synced: int
    sync_id: int
    deleted: int
    created_at: datetime
    update_at: datetime

    class Config:
        from_attributes = True
