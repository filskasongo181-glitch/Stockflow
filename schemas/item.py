from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):

    name                : str
    mark                : Optional[str]   = None
    modele              : Optional[str]   = None

    level               : Optional[int]   = 1

    qty_by_card         : Optional[int]   = 0
    qty_by_box          : Optional[int]   = 0
    minimal_stock       : Optional[int]   = 1

    length              : Optional[float] = None
    width               : Optional[float] = None
    height              : Optional[float] = None

    purchase_price      : Optional[float] = 1
    sale_price_fc       : Optional[float] = 1

    unite_id            : Optional[int]   = 1

    cbm                 : Optional[float] = 1
    sale_price_devise   : Optional[float] = 1

    picture_path        : Optional[str]   = None
    picture_hash        : Optional[str]   = None

    code_barre          : Optional[str]   = None
    category_item       : Optional[int]   = None


class ItemCreate(ItemBase):
    pass


class ItemSync(ItemBase):
    """
    Schéma pour la synchronisation locale → online.
    Contient les infos de sync en plus.
    """
    sync_id     : Optional[int]      = None

    server_id       : Optional[int] = None
    
    deleted     : int = 0
   
    created_at  : Optional[datetime] = None
    update_at   : Optional[datetime] = None


class ItemUpdate(BaseModel):

    name                : Optional[str]   = None
    mark                : Optional[str]   = None
    modele              : Optional[str]   = None

    level               : Optional[int]   = 1

    qty_by_card         : Optional[int]   = 0
    qty_by_box          : Optional[int]   = 0
    minimal_stock       : Optional[int]   = 1

    length              : Optional[float] = None
    width               : Optional[float] = None
    height              : Optional[float] = None

    purchase_price      : Optional[float] = 1
    sale_price_fc       : Optional[float] = 1

    unite_id            : Optional[int]   = None

    cbm                 : Optional[float] = 1
    sale_price_devise   : Optional[float] = 1

    picture_path        : Optional[str]   = None
    picture_hash        : Optional[str]   = None

    code_barre          : Optional[str]   = None
    category_item       : Optional[int]   = None


class ItemResponse(ItemBase):
    id         : int
    synced     : int
    sync_id    : int
    deleted    : int


    created_at : datetime
    update_at  : datetime

    # picture_hash : str | None = None
    picture_data : str | None = None


    class Config:

        from_attributes = True



