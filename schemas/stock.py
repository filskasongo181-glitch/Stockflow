from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class StockBase(BaseModel) :

    item_id         : Optional[int]    = None
    entrepot_id     : Optional[int]    = 1
    stock_actual    : Optional[float]  = None


class StockCreate(StockBase) : 

    pass

class StockSync(StockBase):

    sync_id     : Optional[int] = None

    server_id       : Optional[int] = None

    deleted     : int = 0
    
    created_at  : Optional[datetime] = None
    update_at   : Optional[datetime] = None

class StockUpdate(BaseModel) :

    item_id         : Optional[int]    = None
    entrepot_id     : Optional[int]    = 1
    stock_actual    : Optional[float]  = None

class StockResponse(StockBase) : 

    id              :   int

    synced          : int
    sync_id         : int
    deleted         : int


    created_at      : datetime
    update_at       : datetime

    class config : 

        from_attributes = True
