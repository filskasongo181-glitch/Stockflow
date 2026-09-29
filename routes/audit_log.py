# """
# routes/audit_logs.py  (ou logs.py selon ton include_router)

# Points critiques :
#   1. /sync/... AVANT /{log_id}
#   2. sync/push : match croisé, pas de doublon
#   3. Convention SyncManager :
#        data.sync_id   = id LOCAL
#        data.server_id = id MySQL (0 si nouveau)
# """
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime

# from ..database_online import get_db
# from ..models.audit_log import AuditLog
# from ..schemas.audit_log import AuditLogCreate, AuditLogResponse
# from ..routes.auth import get_current_user
# from ..models.user import User

# router = APIRouter()


# # ============================================================
# # SYNCHRONISATION  (avant les routes dynamiques)
# # ============================================================

# @router.get("/sync/changes", response_model=List[AuditLogResponse])
# def get_changes(
#     since: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """PULL — logs modifiés depuis `since` (YYYY-MM-DD HH:MM:SS)."""
#     try:
#         since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Format attendu : YYYY-MM-DD HH:MM:SS",
#         )
#     return (
#         db.query(AuditLog)
#         .filter(AuditLog.update_at >= since_date)
#         .order_by(AuditLog.update_at.asc())
#         .all()
#     )


# @router.post("/sync/push", response_model=AuditLogResponse)
# def sync_push(
#     data: AuditLogCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     PUSH local → serveur.

#     Matching (anti-doublon) :
#       1) server_id > 0  → AuditLog.id == server_id
#       2) sync_id > 0    → AuditLog.sync_id == sync_id  (id local)
#       3) sinon CREATE avec sync_id = id local
#     """
#     local_id = int(data.sync_id or 0)
#     server_id = int(data.server_id or 0)

#     existing = None
#     if server_id > 0:
#         existing = db.query(AuditLog).filter(AuditLog.id == server_id).first()
#     if existing is None and local_id > 0:
#         existing = db.query(AuditLog).filter(AuditLog.sync_id == local_id).first()

#     # user_id = id SERVEUR (résolu côté local avant envoi)
#     uid = data.user_id if data.user_id is not None else current_user.id
#     if uid:
#         user_exists = db.query(User).filter(User.id == uid).first()
#         if not user_exists:
#             uid = current_user.id

#     if existing:
#         # Mise à jour si plus récent (ou pas de date)
#         should_update = True
#         if data.update_at and existing.update_at and data.update_at <= existing.update_at:
#             should_update = False

#         if should_update:
#             existing.user_id = uid
#             existing.action = data.action or existing.action
#             existing.details = data.details if data.details is not None else existing.details
#             existing.deleted = data.deleted if data.deleted is not None else existing.deleted
#             if local_id > 0:
#                 existing.sync_id = local_id
#             existing.synced = 1
#             if data.update_at:
#                 existing.update_at = data.update_at
#             db.commit()
#             db.refresh(existing)

#         return existing

#     # Création — lien croisé : server.sync_id = id local
#     new_log = AuditLog(
#         user_id=uid,
#         action=data.action or "SYNC",
#         details=data.details or "",
#         synced=1,
#         sync_id=local_id,  # id LOCAL
#         deleted=data.deleted or 0,
#         created_at=data.created_at,
#         update_at=data.update_at,
#     )
#     db.add(new_log)
#     db.commit()
#     db.refresh(new_log)
#     return new_log


# # ============================================================
# # CRUD
# # ============================================================

# @router.get("/", response_model=List[AuditLogResponse])
# def get_all(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     return (
#         db.query(AuditLog)
#         .filter(AuditLog.deleted == 0)
#         .order_by(AuditLog.created_at.desc())
#         .all()
#     )


# @router.get("/user/{user_id}", response_model=List[AuditLogResponse])
# def get_by_user(
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     return (
#         db.query(AuditLog)
#         .filter(AuditLog.user_id == user_id, AuditLog.deleted == 0)
#         .order_by(AuditLog.created_at.desc())
#         .all()
#     )


# @router.post("/", response_model=AuditLogResponse)
# def create(
#     data: AuditLogCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """Création depuis le web — sync_id=0, synced=0 (le local le récupère au pull)."""
#     new_log = AuditLog(
#         user_id=current_user.id,
#         action=data.action,
#         details=data.details,
#         synced=0,
#         sync_id=0,
#         deleted=0,
#     )
#     db.add(new_log)
#     db.commit()
#     db.refresh(new_log)
#     return new_log


# @router.delete("/{log_id}")
# def delete(
#     log_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     log = (
#         db.query(AuditLog)
#         .filter(AuditLog.id == log_id, AuditLog.deleted == 0)
#         .first()
#     )
#     if not log:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Log {log_id} introuvable",
#         )
#     log.deleted = 1
#     log.synced = 0
#     db.commit()
#     return {"message": f"Log {log_id} supprimé"}









"""
routes/audit_logs.py (prefix /logs) — aligné catégories / SyncManager v3
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from database_online import get_db
from models.audit_log import AuditLog
from schemas.audit_log import AuditLogCreate, AuditLogResponse
from routes.auth import get_current_user
from models.user import User

router = APIRouter()


class LinkLocal(BaseModel):
    local_id: int


# ============================================================
# SYNCHRONISATION  (AVANT /{log_id})
# ============================================================

@router.get("/sync/changes", response_model=List[AuditLogResponse])
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
        db.query(AuditLog)
        .filter(AuditLog.update_at >= since_date)
        .order_by(AuditLog.update_at.asc())
        .all()
    )


@router.post("/sync/push", response_model=AuditLogResponse)
def sync_push(
    data: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    local_id = int(getattr(data, "sync_id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)

    existing = None
    if server_id > 0:
        existing = db.query(AuditLog).filter(AuditLog.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(AuditLog).filter(AuditLog.sync_id == local_id).first()

    uid = data.user_id if getattr(data, "user_id", None) is not None else current_user.id
    if uid:
        if not db.query(User).filter(User.id == uid).first():
            uid = current_user.id

    if existing:
        should_update = True
        if data.update_at and existing.update_at and data.update_at <= existing.update_at:
            should_update = False
        if should_update:
            existing.user_id = uid
            existing.action = data.action or existing.action
            existing.details = data.details if data.details is not None else existing.details
            existing.deleted = data.deleted if data.deleted is not None else existing.deleted
            if local_id > 0:
                existing.sync_id = local_id
            existing.synced = 1
            if data.update_at:
                existing.update_at = data.update_at
            db.commit()
            db.refresh(existing)
        return existing

    new_log = AuditLog(
        user_id=uid,
        action=data.action or "SYNC",
        details=data.details or "",
        synced=1,
        sync_id=local_id,
        deleted=data.deleted or 0,
        created_at=getattr(data, "created_at", None),
        update_at=getattr(data, "update_at", None),
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.patch("/{log_id}/link", response_model=AuditLogResponse)
def link_local(
    log_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Log {log_id} introuvable")
    log.sync_id = data.local_id
    log.synced = 1
    db.commit()
    db.refresh(log)
    return log


# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[AuditLogResponse])
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(AuditLog)
        .filter(AuditLog.deleted == 0)
        .order_by(AuditLog.created_at.desc())
        .all()
    )


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
def get_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id, AuditLog.deleted == 0)
        .order_by(AuditLog.created_at.desc())
        .all()
    )


@router.post("/", response_model=AuditLogResponse)
def create(
    data: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_log = AuditLog(
        user_id=current_user.id,
        action=data.action,
        details=data.details,
        synced=0,
        sync_id=0,
        deleted=0,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.delete("/{log_id}")
def delete(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(AuditLog).filter(AuditLog.id == log_id, AuditLog.deleted == 0).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Log {log_id} introuvable")
    log.deleted = 1
    log.synced = 0
    db.commit()
    return {"message": f"Log {log_id} supprimé"}

