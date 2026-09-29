from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MouvementBase(BaseModel):

    item_id     : Optional[int]   = None
    entrepot_id : Optional[int]   = 1
    date        : Optional[str]   = None
    type        : Optional[str]   = None
    nature      : Optional[str]   = None
    raison      : Optional[str]   = None
    qty         : Optional[float] = None
    # user_id     : Optional[int]   = None


class MouvementCreate(MouvementBase):

    pass

class MouvementSync(BaseModel):
    sync_id     : Optional[int] = None

    server_id       : Optional[int] = None

    item_id     : int
    
    entrepot_id : int

    date        : Optional[str] = None
    type        : Optional[str] = None
    nature      : Optional[str] = None
    raison      : Optional[str] = None
    qty         : Optional[float] = None

    deleted     : int = 0

    created_at  : Optional[datetime] = None
    update_at   : Optional[datetime] = None

class MouvementUpdate(BaseModel):

    item_id     : Optional[int]   = None
    entrepot_id : Optional[int]   = 1
    date        : Optional[str]   = None
    type        : Optional[str]   = None
    nature      : Optional[str]   = None
    raison      : Optional[str]   = None
    qty         : Optional[float] = None
    # user_id     : Optional[int]   = None


class MouvementResponse(MouvementBase):

    id         : int
    item_id    : int
    entrepot_id: int
    date       : str
    type       : str
    nature     : str
    raison     : str
    qty        : float

    synced     : int
    sync_id    : int
    deleted    : int


    created_at : datetime
    update_at  : datetime

    class Config:

        from_attributes = True

# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime


class StockAjustmentBase(BaseModel):
    item_id     : Optional[int]   = None
    entrepot_id : Optional[int]   = 1
    date        : Optional[str]   = None
    type        : Optional[str]   = None
    nature      : Optional[str]   = None
    raison      : Optional[str]   = None
    qty         : Optional[float] = None


class StockAjustmentCreate(StockAjustmentBase):
    pass

class StockAjustmentSync(BaseModel):

    sync_id     : int

    item_id     : int
    entrepot_id : int

    date        : Optional[str] = None
    type        : Optional[str] = None
    nature      : Optional[str] = None
    raison      : Optional[str] = None
    qty         : Optional[float] = None

    deleted     : int = 0
    created_at  : Optional[datetime] = None
    update_at   : Optional[datetime] = None



class StockAjustmentUpdate(BaseModel):
    type   : Optional[str]   = None
    nature : Optional[str]   = None
    raison : Optional[str]   = None
    qty    : Optional[float] = None

class StockAjustmentResponse(StockAjustmentBase):
    id         : int
    synced     : int
    sync_id    : int
    deleted    : int
    update_at  : datetime
    created_at : datetime

    class Config:
        from_attributes = True


