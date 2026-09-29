"""
routes/categories.py

Aligné SyncManager v3 :
  payload.sync_id   = id LOCAL  → enregistré dans Server.sync_id
  payload.server_id = id MySQL  → lookup rapide
  réponse.id        = id MySQL  → local.sync_id = response.id

IMPORTANT : /sync/... AVANT /{cat_id}
"""
import base64
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database_online import get_db
from ..models.categorie import Categorie
from ..schemas.categorie import (
    CategorieCreate,
    CategorieUpdate,
    CategorieSync,
    CategorieResponse,
    LinkLocal
)
from ..routes.auth import get_current_user
from ..models.user import User

router = APIRouter()


# ── Helpers icon ─────────────────────────────────────────────

def blob_to_base64(icon) -> Optional[str]:
    if not icon:
        return None
    if isinstance(icon, memoryview):
        icon = icon.tobytes()
    b64 = base64.b64encode(icon).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def base64_to_blob(icon) -> Optional[bytes]:
    if not icon:
        return None
    try:
        if isinstance(icon, str) and icon.startswith("data:") and "," in icon:
            icon = icon.split(",", 1)[1]
        return base64.b64decode(icon)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format de l'icône invalide : {e}",
        )


def cat_to_dict(cat: Categorie) -> dict:
    return {
        "id": cat.id,
        "name": cat.name,
        "description": cat.description,
        "icon": blob_to_base64(cat.icon),
        "synced": cat.synced,
        "sync_id": cat.sync_id,  # = id local si déjà croisé
        "deleted": cat.deleted,
        "created_at": cat.created_at,
        "update_at": cat.update_at,
    }


def _find_existing(db: Session, data: CategorieSync):
    """Match anti-doublon (même logique que users / audit)."""
    existing = None
    server_id = int(data.server_id or 0)
    local_id = int(data.sync_id or 0)

    if server_id > 0:
        existing = db.query(Categorie).filter(Categorie.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(Categorie).filter(Categorie.sync_id == local_id).first()
    if existing is None and data.name:
        existing = (
            db.query(Categorie)
            .filter(Categorie.name == data.name, Categorie.deleted == 0)
            .first()
        )
    return existing


# ============================================================
# SYNCHRONISATION  (AVANT /{cat_id})
# ============================================================

@router.get("/sync/changes", response_model=List[CategorieResponse])
def get_changes(
    since: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """PULL — catégories modifiées depuis `since`."""
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format attendu : YYYY-MM-DD HH:MM:SS",
        )
    cats = (
        db.query(Categorie)
        .filter(Categorie.update_at >= since_date)
        .order_by(Categorie.update_at.asc())
        .all()
    )
    return [cat_to_dict(c) for c in cats]


@router.post("/sync/push", response_model=CategorieResponse)
def sync_push(
    data: CategorieSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PUSH local → serveur (relation croisée).

    - data.sync_id   = id LOCAL  → Server.sync_id
    - data.server_id = id MySQL  → lookup
    - retourne id serveur        → local.sync_id = response.id
    """
    local_id = int(data.sync_id or 0)
    existing = _find_existing(db, data)
    icon_blob = base64_to_blob(data.icon) if data.icon else None

    if existing:
        should_update = True
        if data.update_at and existing.update_at and data.update_at <= existing.update_at:
            should_update = False

        if should_update:
            existing.name = data.name or existing.name
            existing.description = data.description
            if icon_blob is not None:
                existing.icon = icon_blob
            existing.deleted = data.deleted if data.deleted is not None else 0
            existing.synced = 1
            if local_id > 0:
                existing.sync_id = local_id  # ← LIEN CROISÉ (id local)
            if data.update_at:
                existing.update_at = data.update_at
            db.commit()
            db.refresh(existing)

        return cat_to_dict(existing)

    # Création — Server.sync_id = id LOCAL
    new_cat = Categorie(
        name=data.name,
        description=data.description,
        icon=icon_blob,
        synced=1,
        sync_id=local_id,  # ← PAS 0
        deleted=data.deleted or 0,
        created_at=data.created_at,
        update_at=data.update_at,
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return cat_to_dict(new_cat)

@router.patch("/{cat_id}/link", response_model=CategorieResponse)
def link_local(
    cat_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(Categorie).filter(Categorie.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail=f"Catégorie {cat_id} introuvable")
    cat.sync_id = data.local_id
    cat.synced = 1
    db.commit()
    db.refresh(cat)
    return cat_to_dict(cat)

# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[CategorieResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cats = db.query(Categorie).filter(Categorie.deleted == 0).all()
    return [cat_to_dict(c) for c in cats]


@router.get("/{cat_id}", response_model=CategorieResponse)
def get_one(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = (
        db.query(Categorie)
        .filter(Categorie.id == cat_id, Categorie.deleted == 0)
        .first()
    )
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catégorie {cat_id} introuvable",
        )
    return cat_to_dict(cat)


@router.post("/", response_model=CategorieResponse)
def create(
    data: CategorieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Création WEB.
    synced=0, sync_id=0 → le local récupère via /sync/changes
    puis au prochain push local complète la croix (server.sync_id = local.id).
    """
    icon_blob = base64_to_blob(data.icon) if data.icon else None
    
    new_cat = Categorie(
        name=data.name,
        description=data.description,
        icon=icon_blob,
        synced=0,
        sync_id=0,
        deleted=0,
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return cat_to_dict(new_cat)


@router.put("/{cat_id}", response_model=CategorieResponse)
def update(
    cat_id: int,
    data: CategorieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = (
        db.query(Categorie)
        .filter(Categorie.id == cat_id, Categorie.deleted == 0)
        .first()
    )
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catégorie {cat_id} introuvable",
        )
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "icon":
            value = base64_to_blob(value) if value else None
        setattr(cat, field, value)
    cat.synced = 0  # le local reprendra le changement
    db.commit()
    db.refresh(cat)
    return cat_to_dict(cat)


@router.delete("/{cat_id}")
def delete(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = (
        db.query(Categorie)
        .filter(Categorie.id == cat_id, Categorie.deleted == 0)
        .first()
    )
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catégorie {cat_id} introuvable",
        )
    cat.deleted = 1
    cat.synced = 0
    db.commit()
    return {"message": f"Catégorie {cat_id} supprimée"}



