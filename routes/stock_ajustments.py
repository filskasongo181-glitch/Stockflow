# """
# # =========================================== #
# #     ROUTES STOCK AJUSTEMENTS                #
# # =========================================== #
# """
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime
# from ..database_online       import get_db

# from ..models.mouvement import StockAjustment
# from ..models.item             import Item
# from ..models.entrepot         import Entrepot
# from ..schemas.mouvement import (
#     StockAjustmentCreate,
#     StockAjustmentUpdate,
#     StockAjustmentResponse,
#     StockAjustmentSync
# )
# from ..routes.auth             import get_current_user
# from ..models.user             import User


# router = APIRouter()

# # ============================================================
# # CRUD
# # ============================================================

# # GET

# @router.get("/", response_model=List[StockAjustmentResponse])
# def get_all(

#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """Retourne tous les ajustements non supprimés."""
#     return db.query(StockAjustment).filter(

#         StockAjustment.deleted == 0

#     ).order_by(StockAjustment.created_at.desc()).all()

# @router.get("/item/{item_id}", response_model=List[StockAjustmentResponse])
# def get_by_item(

#     item_id      : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """Tous les ajustements d'un article."""
#     return db.query(StockAjustment).filter(

#         StockAjustment.item_id == item_id,
#         StockAjustment.deleted == 0

#     ).order_by(StockAjustment.created_at.desc()).all()

# @router.get("/type/{type_ajust}",response_model=List[StockAjustmentResponse])
# def get_by_type(

#     type_ajust   : str,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """
#     Filtre par type.
#     Exemple : /ajustements/type/depreciation
#               /ajustements/type/regularisation
#     """
#     return db.query(StockAjustment).filter(

#         StockAjustment.type    == type_ajust,
#         StockAjustment.deleted == 0

#     ).order_by(StockAjustment.created_at.desc()).all()

# # ============================================================
# # SYNCHRONISATION
# # ============================================================
# @router.get("/sync/changes", response_model=List[StockAjustmentResponse])
# def get_changes(

#     since        : str,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """PULL — ajustements modifiés depuis une date."""
#     try:

#         since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")

#     except ValueError:

#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Format attendu : YYYY-MM-DD HH:MM:SS"
#         )

#     return db.query(StockAjustment).filter(

#         StockAjustment.update_at >= since_date

#     ).all()

# # POST

# @router.post("/", response_model=StockAjustmentResponse)
# def create(

#     data         : StockAjustmentCreate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """Crée un nouvel ajustement."""
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

#     new_ajust = StockAjustment(
#         item_id     = data.item_id,
#         entrepot_id = data.entrepot_id,
#         date        = data.date,
#         type        = data.type,
#         nature      = data.nature,
#         raison      = data.raison,
#         qty         = data.qty,
#         synced      = 0,
#         sync_id     = 0,
#         deleted     = 0
#     )

#     db.add(new_ajust)

#     db.commit()

#     db.refresh(new_ajust)

#     return new_ajust

# @router.post("/sync/push", response_model=StockAjustmentResponse)
# def sync_push(

#     data         : StockAjustmentSync,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):

#     """PUSH — reçoit un ajustement depuis l'app locale."""
#     new_ajust = StockAjustment(
#         item_id     = data.item_id,
#         entrepot_id = data.entrepot_id,
#         date        = data.date,
#         type        = data.type,
#         nature      = data.nature,
#         raison      = data.raison,
#         qty         = data.qty,
#         synced      = 1,
#         sync_id=data.sync_id or 0,
#         deleted=data.deleted,
#         created_at=data.created_at,
#         update_at=data.update_at
#     )

#     db.add(new_ajust)

#     db.commit()

#     db.refresh(new_ajust)

#     return new_ajust


# # PUT
# @router.put("/{ajust_id}", response_model=StockAjustmentResponse)
# def update(

#     ajust_id     : int,
#     data         : StockAjustmentUpdate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """Modifie un ajustement."""
#     ajust = db.query(StockAjustment).filter(

#         StockAjustment.id      == ajust_id,
#         StockAjustment.deleted == 0

#     ).first()

#     if not ajust:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Ajustement {ajust_id} introuvable"
#         )

#     update_data = data.model_dump(exclude_unset=True)

#     for field, value in update_data.items():

#         setattr(ajust, field, value)

#     ajust.synced = 0

#     db.commit()

#     db.refresh(ajust)

#     return ajust

# # DELETED

# @router.delete("/{ajust_id}")
# def delete(

#     ajust_id     : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """Suppression douce."""
#     ajust = db.query(StockAjustment).filter(

#         StockAjustment.id      == ajust_id,
#         StockAjustment.deleted == 0

#     ).first()

#     if not ajust:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Ajustement {ajust_id} introuvable"
#         )

#     ajust.deleted = 1

#     ajust.synced  = 0

#     db.commit()

#     return {"message": f"Ajustement {ajust_id} supprimé"}

# # GET

# @router.get("/{ajust_id}", response_model=StockAjustmentResponse)
# def get_one(

#     ajust_id     : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """Retourne un ajustement par son ID."""
#     ajust = db.query(StockAjustment).filter(

#         StockAjustment.id      == ajust_id,
#         StockAjustment.deleted == 0
#     ).first()

#     if not ajust:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Ajustement {ajust_id} introuvable"
#         )

#     return ajust






"""
routes/ajustements.py (ou stock_ajustments) — aligné catégories / SyncManager v3

SyncManager :
  GET  /mouvements/ajustements/sync/changes
  POST /mouvements/ajustements/sync/push

Convention :
  payload.sync_id   = id LOCAL
  payload.server_id = id MySQL
  item_id / entrepot_id = ids SERVEUR
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from ..database_online import get_db
from ..models.mouvement import StockAjustment
from ..models.item import Item
from ..models.entrepot import Entrepot
from ..schemas.mouvement import (
    StockAjustmentCreate,
    StockAjustmentUpdate,
    StockAjustmentResponse,
    StockAjustmentSync,
)
from ..routes.auth import get_current_user
from ..models.user import User

router = APIRouter()


class LinkLocal(BaseModel):
    local_id: int


def _check_item_entrepot(db: Session, item_id: int, entrepot_id: int):
    item = db.query(Item).filter(Item.id == item_id, Item.deleted == 0).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {item_id} introuvable",
        )
    entrepot = (
        db.query(Entrepot)
        .filter(Entrepot.id == entrepot_id, Entrepot.deleted == 0)
        .first()
    )
    if not entrepot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entrepôt {entrepot_id} introuvable",
        )


# ============================================================
# SYNCHRONISATION  (AVANT /{ajust_id})
# ============================================================

@router.get("/sync/changes", response_model=List[StockAjustmentResponse])
def get_changes(
    since: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format attendu : YYYY-MM-DD HH:MM:SS",
        )
    return (
        db.query(StockAjustment)
        .filter(StockAjustment.update_at >= since_date)
        .order_by(StockAjustment.update_at.asc())
        .all()
    )


@router.post("/sync/push", response_model=StockAjustmentResponse)
def sync_push(
    data: StockAjustmentSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    local_id = int(getattr(data, "sync_id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)

    _check_item_entrepot(db, data.item_id, data.entrepot_id)

    existing = None
    if server_id > 0:
        existing = db.query(StockAjustment).filter(StockAjustment.id == server_id).first()
    if existing is None and local_id > 0:
        existing = (
            db.query(StockAjustment)
            .filter(StockAjustment.sync_id == local_id)
            .first()
        )

    if existing:
        should_update = True
        if data.update_at and existing.update_at and data.update_at <= existing.update_at:
            should_update = False
        if should_update:
            existing.item_id = data.item_id
            existing.entrepot_id = data.entrepot_id
            existing.date = data.date
            existing.type = data.type
            existing.nature = data.nature
            existing.raison = data.raison
            existing.qty = data.qty
            existing.deleted = data.deleted if data.deleted is not None else 0
            existing.synced = 1
            if local_id > 0:
                existing.sync_id = local_id
            if data.update_at:
                existing.update_at = data.update_at
            db.commit()
            db.refresh(existing)
        return existing

    new_ajust = StockAjustment(
        item_id=data.item_id,
        entrepot_id=data.entrepot_id,
        date=data.date,
        type=data.type,
        nature=data.nature,
        raison=data.raison,
        qty=data.qty,
        synced=1,
        sync_id=local_id,
        deleted=data.deleted or 0,
        created_at=data.created_at,
        update_at=data.update_at,
    )
    db.add(new_ajust)
    db.commit()
    db.refresh(new_ajust)
    return new_ajust


@router.patch("/{ajust_id}/link", response_model=StockAjustmentResponse)
def link_local(
    ajust_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ajust = db.query(StockAjustment).filter(StockAjustment.id == ajust_id).first()
    if not ajust:
        raise HTTPException(status_code=404, detail=f"Ajustement {ajust_id} introuvable")
    ajust.sync_id = data.local_id
    ajust.synced = 1
    db.commit()
    db.refresh(ajust)
    return ajust


# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[StockAjustmentResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(StockAjustment)
        .filter(StockAjustment.deleted == 0)
        .order_by(StockAjustment.created_at.desc())
        .all()
    )


@router.get("/item/{item_id}", response_model=List[StockAjustmentResponse])
def get_by_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(StockAjustment)
        .filter(StockAjustment.item_id == item_id, StockAjustment.deleted == 0)
        .order_by(StockAjustment.created_at.desc())
        .all()
    )


@router.get("/type/{type_ajust}", response_model=List[StockAjustmentResponse])
def get_by_type(
    type_ajust: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(StockAjustment)
        .filter(StockAjustment.type == type_ajust, StockAjustment.deleted == 0)
        .order_by(StockAjustment.created_at.desc())
        .all()
    )


@router.post("/", response_model=StockAjustmentResponse)
def create(
    data: StockAjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_item_entrepot(db, data.item_id, data.entrepot_id)
    new_ajust = StockAjustment(
        item_id=data.item_id,
        entrepot_id=data.entrepot_id,
        date=data.date,
        type=data.type,
        nature=data.nature,
        raison=data.raison,
        qty=data.qty,
        synced=0,
        sync_id=0,
        deleted=0,
    )
    db.add(new_ajust)
    db.commit()
    db.refresh(new_ajust)
    return new_ajust


@router.get("/{ajust_id}", response_model=StockAjustmentResponse)
def get_one(
    ajust_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ajust = (
        db.query(StockAjustment)
        .filter(StockAjustment.id == ajust_id, StockAjustment.deleted == 0)
        .first()
    )
    if not ajust:
        raise HTTPException(status_code=404, detail=f"Ajustement {ajust_id} introuvable")
    return ajust


@router.put("/{ajust_id}", response_model=StockAjustmentResponse)
def update(
    ajust_id: int,
    data: StockAjustmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ajust = (
        db.query(StockAjustment)
        .filter(StockAjustment.id == ajust_id, StockAjustment.deleted == 0)
        .first()
    )
    if not ajust:
        raise HTTPException(status_code=404, detail=f"Ajustement {ajust_id} introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ajust, field, value)
    ajust.synced = 0
    db.commit()
    db.refresh(ajust)
    return ajust


@router.delete("/{ajust_id}")
def delete(
    ajust_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ajust = (
        db.query(StockAjustment)
        .filter(StockAjustment.id == ajust_id, StockAjustment.deleted == 0)
        .first()
    )
    if not ajust:
        raise HTTPException(status_code=404, detail=f"Ajustement {ajust_id} introuvable")
    ajust.deleted = 1
    ajust.synced = 0
    db.commit()
    return {"message": f"Ajustement {ajust_id} supprimé"}
