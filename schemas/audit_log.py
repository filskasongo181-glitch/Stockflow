from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditLogBase(BaseModel):
    action  : str
    details : Optional[str] = None
    user_id: Optional[int]  = None

class AuditLogCreate(AuditLogBase):
    sync_id: Optional[int] = None      # id LOCAL
    server_id: Optional[int] = None    # id MySQL (0 si nouveau)
    deleted: int = 0
    created_at: Optional[datetime] = None
    update_at: Optional[datetime] = None

class AuditLogResponse(BaseModel):
    id         : int
    user_id: Optional[int] = None
    action: str
    details: Optional[str] = None
    synced     : int
    sync_id    : int
    deleted    : int
    update_at  : datetime
    created_at : datetime
    
    class Config:
        from_attributes = True

