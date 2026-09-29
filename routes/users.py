"""
routes/users.py — aligné catégories / SyncManager v3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database_online import get_db
from models.user import User
from schemas.user import PasswordUpdate, UserCreate, UserSync, UserUpdate, UserResponse
from routes.auth import get_current_user, hash_password

router = APIRouter()


class LinkLocal(BaseModel):
    local_id: int


# ============================================================
# SYNCHRONISATION  (AVANT /{user_id})
# ============================================================

@router.get("/sync/changes", response_model=List[UserResponse])
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
        db.query(User)
        .filter(User.update_at >= since_date)
        .order_by(User.update_at.asc())
        .all()
    )


@router.post("/sync/push", response_model=UserResponse)
def sync_push(
    data: UserSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    local_id = int(getattr(data, "sync_id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)

    existing = None
    if server_id > 0:
        existing = db.query(User).filter(User.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(User).filter(User.sync_id == local_id).first()
    if existing is None and data.email:
        existing = (
            db.query(User)
            .filter(User.email == data.email, User.deleted == 0)
            .first()
        )

    if existing:
        should_update = True
        if data.update_at and existing.update_at and data.update_at <= existing.update_at:
            should_update = False
        if should_update:
            existing.name = data.name
            existing.first_name = data.first_name
            existing.middle_name = data.middle_name
            existing.genre = data.genre
            existing.email = data.email
            existing.role = data.role
            if data.password:
                existing.password = data.password  # déjà haché côté local
            existing.deleted = data.deleted if data.deleted is not None else 0
            existing.synced = 1
            if local_id > 0:
                existing.sync_id = local_id
            if data.update_at:
                existing.update_at = data.update_at
            db.commit()
            db.refresh(existing)
        return existing

    new_user = User(
        name=data.name,
        first_name=data.first_name,
        middle_name=data.middle_name,
        genre=data.genre,
        email=data.email,
        role=data.role,
        password=data.password,
        synced=1,
        sync_id=local_id,
        deleted=data.deleted or 0,
        created_at=data.created_at,
        update_at=data.update_at,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/{user_id}/link", response_model=UserResponse)
def link_local(
    user_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Utilisateur {user_id} introuvable")
    user.sync_id = data.local_id
    user.synced = 1
    db.commit()
    db.refresh(user)
    return user


# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[UserResponse])
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).filter(User.deleted == 0).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_one(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id, User.deleted == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Utilisateur {user_id} introuvable")
    return user


@router.post("/", response_model=UserResponse)
def create(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(User)
        .filter(User.email == data.email, User.deleted == 0)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    new_user = User(
        name=data.name,
        first_name=data.first_name,
        middle_name=data.middle_name,
        genre=data.genre,
        email=data.email,
        role=data.role,
        password=hash_password(data.password),
        synced=0,
        sync_id=0,
        deleted=0,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
def update(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id, User.deleted == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Utilisateur {user_id} introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    user.synced = 0
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/password")
def update_password(
    user_id: int,
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = (
        db.query(User)
        .filter(User.id == user_id, User.deleted == 0)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur {user_id} introuvable"
        )

    role = (current_user.role or "").lower()

    if role not in ("admin", "administrateur"):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Vous ne pouvez modifier que votre propre mot de passe",
            )

    user.password = hash_password(data.new_password)
    user.synced = 0

    db.commit()
    db.refresh(user)

    return {"message": "Mot de passe mis à jour"}

@router.delete("/{user_id}")
def delete(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id, User.deleted == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Utilisateur {user_id} introuvable")
    user.deleted = 1
    user.synced = 0
    db.commit()
    return {"message": f"Utilisateur {user_id} supprimé"}
