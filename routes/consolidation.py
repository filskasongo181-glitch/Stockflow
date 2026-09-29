# """
# StockFlow API — Consolidation / Actualisation
# Fichier : backend/routes/consolidation.py

# Dans api.py (point d'entrée) :
#     from backend.routes import consolidation
#     app.include_router(
#         consolidation.router,
#         prefix="/consolidation",
#         tags=["Consolidation"],
#     )

# Endpoint :
#     POST /consolidation/consolider
# """

# from __future__ import annotations

# import logging
# from datetime import datetime, timedelta
# from typing import Optional

# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel, Field
# from sqlalchemy import text
# from sqlalchemy.orm import Session

# from backend.database_online import SessionLocal
# # Si chez toi get_db est déjà défini ailleurs, tu peux remplacer par :
# # from backend.database_online import get_db

# log = logging.getLogger(__name__)
# router = APIRouter()


# class ConsoliderIn(BaseModel):
#     older_than_days: int = Field(120, ge=0, description="120 ≈ 4 mois")
#     cutoff: Optional[str] = Field(
#         None,
#         description="YYYY-MM-DD HH:MM:SS — si omis : maintenant - older_than_days",
#     )


# class ConsoliderOut(BaseModel):
#     ok: bool
#     cutoff: str
#     deleted_recents: int
#     deleted_ajustements: int
#     at: str


# def get_db():
#     if SessionLocal is None:
#         raise HTTPException(status_code=503, detail="Base en ligne non disponible")
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def _parse_cutoff(older_than_days: int, cutoff: Optional[str]) -> datetime:
#     if cutoff:
#         raw = cutoff.strip()
#         for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
#             try:
#                 return datetime.strptime(raw[:19], fmt)
#             except ValueError:
#                 continue
#         raise HTTPException(status_code=400, detail=f"cutoff invalide : {cutoff}")
#     return datetime.now() - timedelta(days=older_than_days)


# def _dt_str(dt: datetime) -> str:
#     return dt.strftime("%Y-%m-%d %H:%M:%S")


# def _hard_delete_before(db: Session, table: str, cutoff_s: str) -> int:
#     """DELETE réel — tables = modèles MouvementRecent / StockAjustment."""
#     sql = text(
#         f"""
#         DELETE FROM {table}
#         WHERE COALESCE(date, created_at, update_at) <= :cutoff
#         """
#     )
#     result = db.execute(sql, {"cutoff": cutoff_s})
#     return int(result.rowcount or 0)


# @router.post("/consolider", response_model=ConsoliderOut)
# def consolider_mouvements(
#     body: ConsoliderIn,
#     db: Session = Depends(get_db),
# ):
#     """
#     Purge réelle côté WEB des mouvements chauds déjà consolidés en local.

#     Client local :
#       1. consolider_stocks()
#       2. synchroniser()
#       3. POST /consolidation/consolider
#     """
#     cutoff_dt = _parse_cutoff(body.older_than_days, body.cutoff)
#     cutoff_s = _dt_str(cutoff_dt)

#     try:
#         deleted_recents = _hard_delete_before(db, "mouvements_recents", cutoff_s)
#         deleted_aj = _hard_delete_before(db, "stock_ajustments", cutoff_s)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         log.exception("Consolidation web échouée")
#         raise HTTPException(status_code=500, detail=str(e))

#     log.info(
#         f"Consolidation web OK — cutoff={cutoff_s} "
#         f"recents={deleted_recents} ajustements={deleted_aj}"
#     )
#     return ConsoliderOut(
#         ok=True,
#         cutoff=cutoff_s,
#         deleted_recents=deleted_recents,
#         deleted_ajustements=deleted_aj,
#         at=_dt_str(datetime.now()),
#     )




"""
StockFlow API — Consolidation / Actualisation
Fichier : backend/routes/consolidation.py

Dans api.py :
    from backend.routes import consolidation
    app.include_router(
        consolidation.router,
        prefix="/consolidation",
        tags=["Consolidation"],
    )

Endpoint :
    POST /consolidation/consolider
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

# Même get_db que mouvements / categories / items (connexion déjà initialisée au startup)
from database_online import get_db

log = logging.getLogger(__name__)
router = APIRouter()


class ConsoliderIn(BaseModel):
    older_than_days: int = Field(120, ge=0, description="120 ≈ 4 mois")
    cutoff: Optional[str] = Field(
        None,
        description="YYYY-MM-DD HH:MM:SS — si omis : maintenant - older_than_days",
    )


class ConsoliderOut(BaseModel):
    ok: bool
    cutoff: str
    deleted_recents: int
    deleted_ajustements: int
    at: str


def _parse_cutoff(older_than_days: int, cutoff: Optional[str]) -> datetime:
    if cutoff:
        raw = cutoff.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw[:19], fmt)
            except ValueError:
                continue
        raise HTTPException(status_code=400, detail=f"cutoff invalide : {cutoff}")
    return datetime.now() - timedelta(days=older_than_days)


def _dt_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _hard_delete_before(db: Session, table: str, cutoff_s: str) -> int:
    """DELETE réel — tables = modèles MouvementRecent / StockAjustment."""
    sql = text(
        f"""
        DELETE FROM {table}
        WHERE COALESCE(date, created_at, update_at) <= :cutoff
        """
    )
    result = db.execute(sql, {"cutoff": cutoff_s})
    return int(result.rowcount or 0)


@router.post("/consolider", response_model=ConsoliderOut)
def consolider_mouvements(
    body: ConsoliderIn,
    db: Session = Depends(get_db),
):
    """
    Purge réelle côté WEB des mouvements chauds déjà consolidés en local.

    Client local :
      1. consolider_stocks()
      2. synchroniser()
      3. POST /consolidation/consolider
    """
    cutoff_dt = _parse_cutoff(body.older_than_days, body.cutoff)
    cutoff_s = _dt_str(cutoff_dt)

    try:
        deleted_recents = _hard_delete_before(db, "mouvements_recents", cutoff_s)
        deleted_aj = _hard_delete_before(db, "stock_ajustments", cutoff_s)
        db.commit()
    except Exception as e:
        db.rollback()
        log.exception("Consolidation web échouée")
        raise HTTPException(status_code=500, detail=str(e))

    log.info(
        f"Consolidation web OK — cutoff={cutoff_s} "
        f"recents={deleted_recents} ajustements={deleted_aj}"
    )
    return ConsoliderOut(
        ok=True,
        cutoff=cutoff_s,
        deleted_recents=deleted_recents,
        deleted_ajustements=deleted_aj,
        at=_dt_str(datetime.now()),
    )
