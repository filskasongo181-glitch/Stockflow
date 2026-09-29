# """
# # =========================================== #
# #     ROUTES ENTREPÔTS                        #
# # =========================================== #
# """
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime
# from ..database_online import get_db
# from ..models.entrepot import Entrepot
# from ..schemas.entrepot import EntrepotCreate, EntrepotSync, EntrepotUpdate, EntrepotResponse
# from ..routes.auth import get_current_user
# from ..models.user import User

# router = APIRouter()

# # ============================================================
# # SYNCHRONISATION
# # ============================================================
# @router.get("/sync/changes", response_model=List[EntrepotResponse])
# def get_changes(
#     since        : str,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     try:
#         since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Format attendu : YYYY-MM-DD HH:MM:SS"
#         )
#     return db.query(Entrepot).filter(
#         Entrepot.update_at >= since_date
#     ).all()

# @router.post("/sync/push", response_model=EntrepotResponse)
# def sync_push(
#     data         : EntrepotSync,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     existing = db.query(Entrepot).filter(
#         Entrepot.reference == data.reference
#     ).first()
#     if existing:

#         return existing
    
#     new_entrepot = Entrepot(
#         reference    = data.reference,
#         description  = data.description,
#         localisation = data.localisation,
#         capacity     = data.capacity,
#         synced       = 1,
#         sync_id=data.sync_id or 0,
#         deleted=data.deleted,
#         created_at=data.created_at,
#         update_at=data.update_at
#     )
#     db.add(new_entrepot)

#     db.commit()

#     db.refresh(new_entrepot)
    
#     return new_entrepot


# # ============================================================
# # CRUD
# # ============================================================
# @router.get("/", response_model=List[EntrepotResponse])
# def get_all(
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     return db.query(Entrepot).filter(
#         Entrepot.deleted == 0
#     ).all()

# @router.get("/{entrepot_id}", response_model=EntrepotResponse)
# def get_one(
#     entrepot_id  : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     entrepot = db.query(Entrepot).filter(
#         Entrepot.id      == entrepot_id,
#         Entrepot.deleted == 0
#     ).first()
#     if not entrepot:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Entrepôt {entrepot_id} introuvable"
#         )
#     return entrepot

# @router.post("/", response_model=EntrepotResponse)
# def create(
#     data         : EntrepotCreate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     existing = db.query(Entrepot).filter(
#         Entrepot.reference == data.reference,
#         Entrepot.deleted   == 0
#     ).first()
#     if existing:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Un entrepôt avec cette référence existe déjà"
#         )
#     new_entrepot = Entrepot(
#         reference    = data.reference,
#         description  = data.description,
#         localisation = data.localisation,
#         capacity     = data.capacity,
#         synced       = 0,
#         sync_id      = 0,
#         deleted      = 0
#     )
#     db.add(new_entrepot)
#     db.commit()
#     db.refresh(new_entrepot)
#     return new_entrepot

# @router.put("/{entrepot_id}", response_model=EntrepotResponse)
# def update(
#     entrepot_id  : int,
#     data         : EntrepotUpdate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     entrepot = db.query(Entrepot).filter(
#         Entrepot.id      == entrepot_id,
#         Entrepot.deleted == 0
#     ).first()

#     if not entrepot:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Entrepôt {entrepot_id} introuvable"
#         )
    
#     update_data = data.model_dump(exclude_unset=True)

#     for field, value in update_data.items():

#         setattr(entrepot, field, value)

#     entrepot.synced = 0

#     db.commit()

#     db.refresh(entrepot)

#     return entrepot

# @router.delete("/{entrepot_id}")
# def delete(
#     entrepot_id  : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     entrepot = db.query(Entrepot).filter(
# Entrepot.id      == entrepot_id,
#         Entrepot.deleted == 0
#     ).first()
#     if not entrepot:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Entrepôt {entrepot_id} introuvable"
#         )
#     entrepot.deleted = 1
#     entrepot.synced  = 0
#     db.commit()
#     return {"message": f"Entrepôt {entrepot_id} supprimé"}



















"""
routes/entrepots.py — aligné catégories / SyncManager v3
  payload.sync_id   = id LOCAL  → Server.sync_id
  payload.server_id = id MySQL
  PATCH /{id}/link  → ferme la croix après PULL web
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database_online import get_db
from models.entrepot import Entrepot
from schemas.entrepot import (
    EntrepotCreate, EntrepotSync, EntrepotUpdate, EntrepotResponse,
)
from routes.auth import get_current_user
from models.user import User

router = APIRouter()


class LinkLocal(BaseModel):
    local_id: int


# ============================================================
# SYNCHRONISATION  (AVANT /{entrepot_id})
# ============================================================

@router.get("/sync/changes", response_model=List[EntrepotResponse])
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
        db.query(Entrepot)
        .filter(Entrepot.update_at >= since_date)
        .order_by(Entrepot.update_at.asc())
        .all()
    )


@router.post("/sync/push", response_model=EntrepotResponse)
def sync_push(
    data: EntrepotSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    local_id = int(getattr(data, "sync_id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)

    existing = None
    if server_id > 0:
        existing = db.query(Entrepot).filter(Entrepot.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(Entrepot).filter(Entrepot.sync_id == local_id).first()
    if existing is None and data.reference:
        existing = (
            db.query(Entrepot)
            .filter(Entrepot.reference == data.reference)
            .first()
        )

    if existing:
        should_update = True
        if data.update_at and existing.update_at and data.update_at <= existing.update_at:
            should_update = False
        if should_update:
            existing.reference = data.reference
            existing.description = data.description
            existing.localisation = data.localisation
            existing.capacity = data.capacity
            existing.deleted = data.deleted if data.deleted is not None else 0
            existing.synced = 1
            if local_id > 0:
                existing.sync_id = local_id
            if data.update_at:
                existing.update_at = data.update_at
            db.commit()
            db.refresh(existing)
        return existing

    new_entrepot = Entrepot(
        reference=data.reference,
        description=data.description,
        localisation=data.localisation,
        capacity=data.capacity,
        synced=1,
        sync_id=local_id,
        deleted=data.deleted or 0,
        created_at=data.created_at,
        update_at=data.update_at,
    )
    db.add(new_entrepot)
    db.commit()
    db.refresh(new_entrepot)
    return new_entrepot


@router.patch("/{entrepot_id}/link", response_model=EntrepotResponse)
def link_local(
    entrepot_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entrepot = db.query(Entrepot).filter(Entrepot.id == entrepot_id).first()
    if not entrepot:
        raise HTTPException(status_code=404, detail=f"Entrepôt {entrepot_id} introuvable")
    entrepot.sync_id = data.local_id
    entrepot.synced = 1
    db.commit()
    db.refresh(entrepot)
    return entrepot


# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[EntrepotResponse])
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Entrepot).filter(Entrepot.deleted == 0).all()


@router.get("/{entrepot_id}", response_model=EntrepotResponse)
def get_one(
    entrepot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entrepot = (
        db.query(Entrepot)
        .filter(Entrepot.id == entrepot_id, Entrepot.deleted == 0)
        .first()
    )
    if not entrepot:
        raise HTTPException(status_code=404, detail=f"Entrepôt {entrepot_id} introuvable")
    return entrepot


@router.post("/", response_model=EntrepotResponse)
def create(
    data: EntrepotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Entrepot)
        .filter(Entrepot.reference == data.reference, Entrepot.deleted == 0)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Un entrepôt avec cette référence existe déjà",
        )
    new_entrepot = Entrepot(
        reference=data.reference,
        description=data.description,
        localisation=data.localisation,
        capacity=data.capacity,
        synced=0,
        sync_id=0,
        deleted=0,
    )
    db.add(new_entrepot)
    db.commit()
    db.refresh(new_entrepot)
    return new_entrepot


@router.put("/{entrepot_id}", response_model=EntrepotResponse)
def update(
    entrepot_id: int,
    data: EntrepotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entrepot = (
        db.query(Entrepot)
        .filter(Entrepot.id == entrepot_id, Entrepot.deleted == 0)
        .first()
    )
    if not entrepot:
        raise HTTPException(status_code=404, detail=f"Entrepôt {entrepot_id} introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entrepot, field, value)
    entrepot.synced = 0
    db.commit()
    db.refresh(entrepot)
    return entrepot


@router.delete("/{entrepot_id}")
def delete(
    entrepot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entrepot = (
        db.query(Entrepot)
        .filter(Entrepot.id == entrepot_id, Entrepot.deleted == 0)
        .first()
    )
    if not entrepot:
        raise HTTPException(status_code=404, detail=f"Entrepôt {entrepot_id} introuvable")
    entrepot.deleted = 1
    entrepot.synced = 0
    db.commit()
    return {"message": f"Entrepôt {entrepot_id} supprimé"}
