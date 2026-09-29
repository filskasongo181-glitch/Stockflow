# """
# # =========================================== #
# #     ROUTES STOCKS                           #
# # =========================================== #
# """
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from ..database_online import get_db
# from ..models.stock import Stock
# from ..models.item import Item
# from ..models.entrepot import Entrepot
# from ..schemas.stock import StockCreate, StockUpdate, StockResponse, StockSync
# from ..routes.auth import get_current_user
# from ..models.user import User

# router = APIRouter()
# # ============================================================
# # CRUD
# # ============================================================
# @router.get("/", response_model=List[StockResponse])
# def get_all(
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     return db.query(Stock).all()

# @router.get("/item/{item_id}", response_model=List[StockResponse])
# def get_by_item(
#     item_id      : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     """Stock d'un article dans tous les entrepôts."""
#     return db.query(Stock).filter(
#         Stock.item_id == item_id
#     ).all()

# @router.get("/entrepot/{entrepot_id}", response_model=List[StockResponse])
# def get_by_entrepot(
#     entrepot_id  : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     """Tous les stocks d'un entrepôt."""
#     return db.query(Stock).filter(
#         Stock.entrepot_id == entrepot_id
#     ).all()

# @router.get("/item/{item_id}/entrepot/{entrepot_id}", response_model=StockResponse)
# def get_stock_exact(
#     item_id      : int,
#     entrepot_id  : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     """Stock exact d'un article dans un entrepôt précis."""
#     stock = db.query(Stock).filter(
#         Stock.item_id     == item_id,
#         Stock.entrepot_id == entrepot_id
#     ).first()
#     if not stock:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Stock introuvable pour cet article et cet entrepôt"
#         )
#     return stock

# @router.post("/", response_model=StockResponse)
# def create(
#     data         : StockCreate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     # Vérifier article
#     item = db.query(Item).filter(
#         Item.id      == data.item_id,
#         Item.deleted == 0
#     ).first()
#     if not item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Article {data.item_id} introuvable"
#         )
#     # Vérifier entrepôt
#     entrepot = db.query(Entrepot).filter(
#         Entrepot.id      == data.entrepot_id,
#         Entrepot.deleted == 0
#     ).first()
#     if not entrepot:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Entrepôt {data.entrepot_id} introuvable"
#         )
#     # Vérifier si le stock existe déjà
#     existing = db.query(Stock).filter(
#         Stock.item_id     == data.item_id,
#         Stock.entrepot_id == data.entrepot_id
#     ).first()
#     if existing:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Un stock existe déjà pour cet article dans cet entrepôt"
#         )
#     new_stock = Stock(
#         item_id      = data.item_id,
#         entrepot_id  = data.entrepot_id,
#         stock_actual = data.stock_actual
#     )
#     db.add(new_stock)
#     db.commit()
#     db.refresh(new_stock)
#     return new_stock

# @router.put("/item/{item_id}/entrepot/{entrepot_id}", response_model=StockResponse)
# def update_stock(
#     item_id      : int,
#     entrepot_id  : int,
#     data         : StockUpdate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     """Met à jour le stock actuel."""
#     stock = db.query(Stock).filter(
#         Stock.item_id     == item_id,
#         Stock.entrepot_id == entrepot_id
#     ).first()
#     if not stock:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Stock introuvable"
#         )
#     stock.stock_actual = data.stock_actual
#     db.commit()
#     db.refresh(stock)
#     return stock
# # ============================================================
# # SYNCHRONISATION
# # ============================================================
# @router.get("/sync/changes", response_model=List[StockResponse])
# def get_changes(
#     since        : str,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     """PULL — stocks modifiés depuis une date."""
#     from datetime import datetime
#     try:
#         since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Format attendu : YYYY-MM-DD HH:MM:SS"
#         )
#     # Stock n'a pas de update_at → on retourne tout
#     return db.query(Stock).all()

# @router.post("/sync/push", response_model=StockResponse)
# def sync_push(
#     data         : StockSync,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     """PUSH — reçoit un stock depuis l'app locale."""
#     existing = db.query(Stock).filter(
#         Stock.item_id     == data.item_id,
#         Stock.entrepot_id == data.entrepot_id
#     ).first()
#     if existing:
#         # Mettre à jour le stock existant
#         existing.stock_actual = data.stock_actual
#         db.commit()
#         db.refresh(existing)
#         return existing
#     new_stock = Stock(
#         item_id      = data.item_id,
#         entrepot_id  = data.entrepot_id,
#         stock_actual = data.stock_actual,
#         synced = 1,
#         sync_id=data.sync_id or 0,
#         deleted=data.deleted,
#         created_at=data.created_at,
#         update_at=data.update_at
#     )
#     db.add(new_stock)
#     db.commit()
#     db.refresh(new_stock)
#     return new_stock











"""
routes/stocks.py — aligné catégories / SyncManager v3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database_online import get_db
from models.stock import Stock
from models.item import Item
from models.entrepot import Entrepot
from schemas.stock import StockCreate, StockUpdate, StockResponse, StockSync
from routes.auth import get_current_user
from models.user import User

router = APIRouter()


class LinkLocal(BaseModel):
    local_id: int


# ============================================================
# SYNCHRONISATION  (AVANT routes dynamiques)
# ============================================================

@router.get("/sync/changes", response_model=List[StockResponse])
def get_changes(
    since: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format attendu : YYYY-MM-DD HH:MM:SS")
    # Si Stock n'a pas update_at fiable, filtrer quand même si la colonne existe
    q = db.query(Stock)
    if hasattr(Stock, "update_at"):
        q = q.filter(Stock.update_at >= since_date)
    return q.all()


@router.post("/sync/push", response_model=StockResponse)
def sync_push(
    data: StockSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    local_id = int(getattr(data, "sync_id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)

    existing = None
    if server_id > 0:
        existing = db.query(Stock).filter(Stock.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(Stock).filter(Stock.sync_id == local_id).first()
    if existing is None:
        existing = (
            db.query(Stock)
            .filter(
                Stock.item_id == data.item_id,
                Stock.entrepot_id == data.entrepot_id,
            )
            .first()
        )

    if existing:
        existing.stock_actual = data.stock_actual
        existing.item_id = data.item_id
        existing.entrepot_id = data.entrepot_id
        existing.deleted = data.deleted if data.deleted is not None else 0
        existing.synced = 1
        if local_id > 0:
            existing.sync_id = local_id
        db.commit()
        db.refresh(existing)
        return existing

    new_stock = Stock(
        item_id=data.item_id,
        entrepot_id=data.entrepot_id,
        stock_actual=data.stock_actual,
        synced=1,
        sync_id=local_id,
        deleted=data.deleted or 0,
        created_at=getattr(data, "created_at", None),
        update_at=getattr(data, "update_at", None),
    )
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock


@router.patch("/{stock_id}/link", response_model=StockResponse)
def link_local(
    stock_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {stock_id} introuvable")
    stock.sync_id = data.local_id
    stock.synced = 1
    db.commit()
    db.refresh(stock)
    return stock


# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[StockResponse])
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Stock).all()


@router.get("/item/{item_id}", response_model=List[StockResponse])
def get_by_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Stock).filter(Stock.item_id == item_id).all()


@router.get("/entrepot/{entrepot_id}", response_model=List[StockResponse])
def get_by_entrepot(
    entrepot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Stock).filter(Stock.entrepot_id == entrepot_id).all()


@router.get("/item/{item_id}/entrepot/{entrepot_id}", response_model=StockResponse)
def get_stock_exact(
    item_id: int,
    entrepot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock = (
        db.query(Stock)
        .filter(Stock.item_id == item_id, Stock.entrepot_id == entrepot_id)
        .first()
    )
    if not stock:
        raise HTTPException(status_code=404, detail="Stock introuvable")
    return stock


@router.post("/", response_model=StockResponse)
def create(
    data: StockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == data.item_id, Item.deleted == 0).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Article {data.item_id} introuvable")
    entrepot = (
        db.query(Entrepot)
        .filter(Entrepot.id == data.entrepot_id, Entrepot.deleted == 0)
        .first()
    )
    if not entrepot:
        raise HTTPException(status_code=404, detail=f"Entrepôt {data.entrepot_id} introuvable")
    existing = (
        db.query(Stock)
        .filter(Stock.item_id == data.item_id, Stock.entrepot_id == data.entrepot_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Un stock existe déjà pour cet article dans cet entrepôt")
    new_stock = Stock(
        item_id=data.item_id,
        entrepot_id=data.entrepot_id,
        stock_actual=data.stock_actual,
        synced=0,
        sync_id=0,
        deleted=0,
    )
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock


@router.put("/item/{item_id}/entrepot/{entrepot_id}", response_model=StockResponse)
def update_stock(
    item_id: int,
    entrepot_id: int,
    data: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock = (
        db.query(Stock)
        .filter(Stock.item_id == item_id, Stock.entrepot_id == entrepot_id)
        .first()
    )
    if not stock:
        raise HTTPException(status_code=404, detail="Stock introuvable")
    stock.stock_actual = data.stock_actual
    stock.synced = 0
    db.commit()
    db.refresh(stock)
    return stock
