# """
# # =========================================== #
# #     ROUTES UNITÉS                           #
# # =========================================== #
# """
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime
# from ..database_online import get_db
# from ..models.unite import Unite
# from ..schemas.unite import UniteCreate, UniteUpdate, UniteResponse, UniteSync
# from ..routes.auth import get_current_user
# from ..models.user import User


# router = APIRouter()
# # ============================================================
# # CRUD
# # ============================================================
# @router.get("/", response_model=List[UniteResponse])
# def get_all(
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     return db.query(Unite).filter(
#         Unite.deleted == 0
#     ).all()

# @router.get("/{unite_id}", response_model=UniteResponse)
# def get_one(
#     unite_id     : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     unite = db.query(Unite).filter(
# Unite.id      == unite_id,
#         Unite.deleted == 0
#     ).first()
#     if not unite:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Unité {unite_id} introuvable"
#         )
#     return unite

# @router.post("/", response_model=UniteResponse)
# def create(
#     data         : UniteCreate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     new_unite = Unite(
#         niveau_1 = data.niveau_1,
#         niveau_2 = data.niveau_2,
#         niveau_3 = data.niveau_3,
#         synced   = 0,
#         sync_id  = 0,
#         deleted  = 0
#     )
#     db.add(new_unite)
#     db.commit()
#     db.refresh(new_unite)
#     return new_unite

# @router.put("/{unite_id}", response_model=UniteResponse)
# def update(
#     unite_id     : int,
#     data         : UniteUpdate,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     unite = db.query(Unite).filter(
# Unite.id      == unite_id,
#         Unite.deleted == 0
#     ).first()
#     if not unite:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Unité {unite_id} introuvable"
#         )
#     update_data = data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(unite, field, value)
#     unite.synced = 0
#     db.commit()
#     db.refresh(unite)
#     return unite

# @router.delete("/{unite_id}")
# def delete(
#     unite_id     : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     unite = db.query(Unite).filter(
# Unite.id      == unite_id,
#         Unite.deleted == 0
#     ).first()
#     if not unite:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Unité {unite_id} introuvable"
#         )
#     unite.deleted = 1
#     unite.synced  = 0
#     db.commit()
#     return {"message": f"Unité {unite_id} supprimée"}

# # ============================================================
# # SYNCHRONISATION
# # ============================================================
# @router.get("/sync/changes", response_model=List[UniteResponse])
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
#     return db.query(Unite).filter(
#         Unite.update_at >= since_date
#     ).all()

# @router.post("/sync/push", response_model=UniteResponse)
# def sync_push(
#     data         : UniteSync,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)
# ):
#     new_unite = Unite(
#         niveau_1 = data.niveau_1,
#         niveau_2 = data.niveau_2,
#         niveau_3 = data.niveau_3,
#         synced   = 1,
#         sync_id=data.sync_id or 0,
#         deleted=data.deleted,
#         created_at=data.created_at,
#         update_at=data.update_at
#     )
#     db.add(new_unite)
#     db.commit()
#     db.refresh(new_unite)
#     return new_unite


















































"""
routes/unites.py — aligné catégories / SyncManager v3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from ..database_online import get_db
from ..models.unite import Unite
from ..schemas.unite import UniteCreate, UniteUpdate, UniteResponse, UniteSync
from ..routes.auth import get_current_user
from ..models.user import User

router = APIRouter()


class LinkLocal(BaseModel):
    local_id: int


# ============================================================
# SYNCHRONISATION  (AVANT /{unite_id})
# ============================================================

@router.get("/sync/changes", response_model=List[UniteResponse])
def get_changes(
    since: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format attendu : YYYY-MM-DD HH:MM:SS")
    return (
        db.query(Unite)
        .filter(Unite.update_at >= since_date)
        .order_by(Unite.update_at.asc())
        .all()
    )


@router.post("/sync/push", response_model=UniteResponse)
def sync_push(
    data: UniteSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    local_id = int(getattr(data, "sync_id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)

    existing = None
    if server_id > 0:
        existing = db.query(Unite).filter(Unite.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(Unite).filter(Unite.sync_id == local_id).first()

    if existing:
        should_update = True
        if data.update_at and existing.update_at and data.update_at <= existing.update_at:
            should_update = False
        if should_update:
            existing.niveau_1 = data.niveau_1
            existing.niveau_2 = data.niveau_2
            existing.niveau_3 = data.niveau_3
            existing.deleted = data.deleted if data.deleted is not None else 0
            existing.synced = 1
            if local_id > 0:
                existing.sync_id = local_id
            if data.update_at:
                existing.update_at = data.update_at
            db.commit()
            db.refresh(existing)
        return existing

    new_unite = Unite(
        niveau_1=data.niveau_1,
        niveau_2=data.niveau_2,
        niveau_3=data.niveau_3,
        synced=1,
        sync_id=local_id,
        deleted=data.deleted or 0,
        created_at=data.created_at,
        update_at=data.update_at,
    )
    db.add(new_unite)
    db.commit()
    db.refresh(new_unite)
    return new_unite


@router.patch("/{unite_id}/link", response_model=UniteResponse)
def link_local(
    unite_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unite = db.query(Unite).filter(Unite.id == unite_id).first()
    if not unite:
        raise HTTPException(status_code=404, detail=f"Unité {unite_id} introuvable")
    unite.sync_id = data.local_id
    unite.synced = 1
    db.commit()
    db.refresh(unite)
    return unite


# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[UniteResponse])
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Unite).filter(Unite.deleted == 0).all()


@router.get("/{unite_id}", response_model=UniteResponse)
def get_one(
    unite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unite = db.query(Unite).filter(Unite.id == unite_id, Unite.deleted == 0).first()
    if not unite:
        raise HTTPException(status_code=404, detail=f"Unité {unite_id} introuvable")
    return unite


@router.post("/", response_model=UniteResponse)
def create(
    data: UniteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_unite = Unite(
        niveau_1=data.niveau_1,
        niveau_2=data.niveau_2,
        niveau_3=data.niveau_3,
        synced=0,
        sync_id=0,
        deleted=0,
    )
    db.add(new_unite)
    db.commit()
    db.refresh(new_unite)
    return new_unite


@router.put("/{unite_id}", response_model=UniteResponse)
def update(
    unite_id: int,
    data: UniteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unite = db.query(Unite).filter(Unite.id == unite_id, Unite.deleted == 0).first()
    if not unite:
        raise HTTPException(status_code=404, detail=f"Unité {unite_id} introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(unite, field, value)
    unite.synced = 0
    db.commit()
    db.refresh(unite)
    return unite


@router.delete("/{unite_id}")
def delete(
    unite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unite = db.query(Unite).filter(Unite.id == unite_id, Unite.deleted == 0).first()
    if not unite:
        raise HTTPException(status_code=404, detail=f"Unité {unite_id} introuvable")
    unite.deleted = 1
    unite.synced = 0
    db.commit()
    return {"message": f"Unité {unite_id} supprimée"}
