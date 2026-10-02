# """
# # =========================================== #
# #     ROUTES MOUVEMENTS                       #
# # =========================================== #
# """
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime
# from ..database_online import get_db
# from ..models.mouvement          import MouvementRecent
# from ..models.mouvement          import MouvementArchived
# from ..models.mouvement          import StockAjustment
# from ..models.item               import Item
# from ..models.entrepot           import Entrepot
# from ..schemas.mouvement         import MouvementCreate, MouvementUpdate, MouvementResponse, MouvementSync
# from ..routes.auth               import get_current_user
# from ..models.user               import User

# router = APIRouter()

# # ============================================================
# # MOUVEMENTS RÉCENTS
# # ============================================================
# @router.get("/recents", response_model=List[MouvementResponse])
# def get_recents(

#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     return db.query(MouvementRecent).filter(

#         MouvementRecent.deleted == 0

#     ).order_by(MouvementRecent.created_at.desc()).all()

# @router.get("/recents/item/{item_id}", response_model=List[MouvementResponse])
# def get_recents_by_item(

#     item_id      : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     """Historique des mouvements d'un article."""
#     return db.query(MouvementRecent).filter(

#         MouvementRecent.item_id == item_id,
#         MouvementRecent.deleted == 0

#     ).order_by(MouvementRecent.created_at.desc()).all()

# @router.post("/recents", response_model=MouvementResponse)
# def create_recent(

#     data         : MouvementCreate,
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
    
#     new_mvt = MouvementRecent(
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

#     db.add(new_mvt)

#     db.commit()

#     db.refresh(new_mvt)

#     return new_mvt

# @router.delete("/recents/{mvt_id}")
# def delete_recent(

#     mvt_id       : int,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     mvt = db.query(MouvementRecent).filter(

#         MouvementRecent.id      == mvt_id,
#         MouvementRecent.deleted == 0

#     ).first()

#     if not mvt:

#         raise HTTPException(

#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Mouvement {mvt_id} introuvable"

#         )

#     mvt.deleted = 1
#     mvt.synced  = 0
#     db.commit()

#     return {"message": f"Mouvement {mvt_id} supprimé"}

# @router.get("/sync/changes/recent", response_model=List[MouvementResponse])
# def sync_recents(

#     since        : str,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     try:

#         since_date = datetime.strptime(
#             since,
#             "%Y-%m-%d %H:%M:%S"
#         )

#     except ValueError:

#         raise HTTPException(

#             status_code=400,
#             detail="Format attendu : YYYY-MM-DD HH:MM:SS"
        
#         )


#     return db.query(MouvementRecent).filter(

#         MouvementRecent.update_at >= since_date

#     ).all()

# @router.get("/sync/changes/archived", response_model=List[MouvementResponse])
# def sync_archives(

#     since        : str,
#     db           : Session = Depends(get_db),
#     current_user : User    = Depends(get_current_user)

# ):
#     try:

#         since_date = datetime.strptime(
#             since,
#             "%Y-%m-%d %H:%M:%S"
#         )

#     except ValueError:

#         raise HTTPException(

#             status_code=400,
#             detail="Format attendu : YYYY-MM-DD HH:MM:SS"
#         )

#     return db.query(MouvementArchived).filter(

#         MouvementArchived.update_at >= since_date

#     ).all()

# @router.post("/sync/push/recent",response_model=MouvementResponse)
# def sync_push_recent(
#     data: MouvementSync,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     item = db.query(Item).filter(
#         Item.id == data.item_id,
#         Item.deleted == 0
#     ).first()

#     if not item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Article {data.item_id} introuvable"
#         )

#     entrepot = db.query(Entrepot).filter(
#         Entrepot.id == data.entrepot_id,
#         Entrepot.deleted == 0
#     ).first()

#     if not entrepot:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Entrepôt {data.entrepot_id} introuvable"
#         )

#     new_mvt = MouvementRecent(
#         item_id=data.item_id,
#         entrepot_id=data.entrepot_id,
#         date=data.date,
#         type=data.type,
#         nature=data.nature,
#         raison=data.raison,
#         qty=data.qty,
#         synced=1,
#         sync_id=data.sync_id or 0,
#         deleted=data.deleted,
#         created_at=data.created_at,
#         update_at=data.update_at
#     )

#     db.add(new_mvt)
#     db.commit()
#     db.refresh(new_mvt)

#     return new_mvt

# @router.post("/sync/push/archived",response_model=MouvementResponse)
# def sync_push_archived(
#     data: MouvementSync,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     item = db.query(Item).filter(
#         Item.id == data.item_id,
#         Item.deleted == 0
#     ).first()

#     if not item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Article {data.item_id} introuvable"
#         )

#     entrepot = db.query(Entrepot).filter(
#         Entrepot.id == data.entrepot_id,
#         Entrepot.deleted == 0
#     ).first()

#     if not entrepot:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Entrepôt {data.entrepot_id} introuvable"
#         )

#     new_mvt = MouvementArchived(
#         item_id=data.item_id,
#         entrepot_id=data.entrepot_id,
#         date=data.date,
#         type=data.type,
#         nature=data.nature,
#         raison=data.raison,
#         qty=data.qty,
#         synced=1,
#         sync_id=data.sync_id or 0,
#         deleted=data.deleted,
#         created_at=data.created_at,
#         update_at=data.update_at
#     )

#     db.add(new_mvt)
#     db.commit()
#     db.refresh(new_mvt)

#     return new_mvt






"""
routes/mouvements.py — aligné catégories / SyncManager v3

Endpoints SyncManager :
  GET  /mouvements/sync/changes/recent
  GET  /mouvements/sync/changes/archived
  POST /mouvements/sync/push/recent
  POST /mouvements/sync/push/archived

Convention :
  payload.sync_id   = id LOCAL  → Server.sync_id
  payload.server_id = id MySQL
  item_id / entrepot_id = ids SERVEUR (résolus côté local)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database_online import get_db
from models.mouvement import MouvementRecent, MouvementArchived
from models.item import Item
from models.entrepot import Entrepot
from schemas.mouvement import (
    MouvementCreate,
    MouvementUpdate,
    MouvementResponse,
    MouvementSync,
)
from routes.auth import get_current_user
from models.user import User

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
    return item, entrepot


def _sync_push_model(Model, data: MouvementSync, db: Session):
    """Logique commune recent / archived."""
    local_id = int(getattr(data, "sync_id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)

    _check_item_entrepot(db, data.item_id, data.entrepot_id)

    existing = None
    if server_id > 0:
        existing = db.query(Model).filter(Model.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(Model).filter(Model.sync_id == local_id).first()

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

    new_mvt = Model(
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
    db.add(new_mvt)
    db.commit()
    db.refresh(new_mvt)
    return new_mvt


# ============================================================
# SYNCHRONISATION  (avant les routes dynamiques trop larges)
# ============================================================

@router.get("/sync/changes/recent", response_model=List[MouvementResponse])
def sync_recents(
    since: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format attendu : YYYY-MM-DD HH:MM:SS")
    return (
        db.query(MouvementRecent)
        .filter(MouvementRecent.update_at >= since_date)
        .order_by(MouvementRecent.update_at.asc())
        .all()
    )


@router.get("/sync/changes/archived", response_model=List[MouvementResponse])
def sync_archives(
    since: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format attendu : YYYY-MM-DD HH:MM:SS")
    return (
        db.query(MouvementArchived)
        .filter(MouvementArchived.update_at >= since_date)
        .order_by(MouvementArchived.update_at.asc())
        .all()
    )


@router.post("/sync/push/recent", response_model=MouvementResponse)
def sync_push_recent(
    data: MouvementSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _sync_push_model(MouvementRecent, data, db)


@router.post("/sync/push/archived", response_model=MouvementResponse)
def sync_push_archived(
    data: MouvementSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _sync_push_model(MouvementArchived, data, db)


@router.patch("/recents/{mvt_id}/link", response_model=MouvementResponse)
def link_recent(
    mvt_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mvt = db.query(MouvementRecent).filter(MouvementRecent.id == mvt_id).first()
    if not mvt:
        raise HTTPException(status_code=404, detail=f"Mouvement {mvt_id} introuvable")
    mvt.sync_id = data.local_id
    mvt.synced = 1
    db.commit()
    db.refresh(mvt)
    return mvt


@router.patch("/archived/{mvt_id}/link", response_model=MouvementResponse)
def link_archived(
    mvt_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mvt = db.query(MouvementArchived).filter(MouvementArchived.id == mvt_id).first()
    if not mvt:
        raise HTTPException(status_code=404, detail=f"Mouvement archivé {mvt_id} introuvable")
    mvt.sync_id = data.local_id
    mvt.synced = 1
    db.commit()
    db.refresh(mvt)
    return mvt


# ============================================================
# MOUVEMENTS RÉCENTS — CRUD
# ============================================================

@router.get("/recents", response_model=List[MouvementResponse])
def get_recents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(MouvementRecent)
        .filter(MouvementRecent.deleted == 0)
        .order_by(MouvementRecent.created_at.desc())
        .all()
    )


@router.get("/recents/item/{item_id}", response_model=List[MouvementResponse])
def get_recents_by_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(MouvementRecent)
        .filter(MouvementRecent.item_id == item_id, MouvementRecent.deleted == 0)
        .order_by(MouvementRecent.created_at.desc())
        .all()
    )


@router.post("/recents", response_model=MouvementResponse)
def create_recent(
    data: MouvementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_item_entrepot(db, data.item_id, data.entrepot_id)
    new_mvt = MouvementRecent(
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
    db.add(new_mvt)
    db.commit()
    db.refresh(new_mvt)
    return new_mvt


@router.delete("/recents/{mvt_id}")
def delete_recent(
    mvt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mvt = (
        db.query(MouvementRecent)
        .filter(MouvementRecent.id == mvt_id, MouvementRecent.deleted == 0)
        .first()
    )
    if not mvt:
        raise HTTPException(status_code=404, detail=f"Mouvement {mvt_id} introuvable")
    mvt.deleted = 1
    mvt.synced = 0
    db.commit()
    return {"message": f"Mouvement {mvt_id} supprimé"}



# ============================================================
# ARCHIVES (CRUD archives)
# ============================================================

@router.get("/archived", response_model=List[MouvementResponse])
def get_archived(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste tous les mouvements archivés (deleted=0)."""
    return (
        db.query(MouvementArchived)
        .filter(MouvementArchived.deleted == 0)
        .order_by(MouvementArchived.created_at.desc())
        .all()
    )


@router.get("/archived/item/{item_id}", response_model=List[MouvementResponse])
def get_archived_by_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(MouvementArchived)
        .filter(MouvementArchived.item_id == item_id, MouvementArchived.deleted == 0)
        .order_by(MouvementArchived.created_at.desc())
        .all()
    )
