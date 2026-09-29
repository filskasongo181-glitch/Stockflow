"""
GET minimaux — stocks / mouvements_recents / stock_ajustments
=============================================================
À adapter (noms de modèles SQLAlchemy) puis inclure dans main.py :

    from .routes.stocks_min import router as stocks_router
    app.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
    ...
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Any

# Adapte ces imports à ton projet :
from ..database_online import get_db
from ..routes.auth import get_current_user
from ..models.user import User

router_stocks = APIRouter()
router_mouvements = APIRouter()
router_ajustments = APIRouter()


# ---------------------------------------------------------------------------
# STOCKS
# Table typique : stocks (id, item_id, entrepot_id, stock_actual, deleted, ...)
# ---------------------------------------------------------------------------
@router_stocks.get("/")
def list_stocks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Any]:
    rows = db.execute(
        text(
            """
            SELECT id, item_id, entrepot_id, stock_actual, deleted
            FROM stocks
            WHERE IFNULL(deleted, 0) = 0
            """
        )
    ).mappings().all()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# MOUVEMENTS RÉCENTS
# Adapte les noms de colonnes si besoin (quantite, qte, type_mouvement…)
# ---------------------------------------------------------------------------
@router_mouvements.get("/")
def list_mouvements_recents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Any]:
    rows = db.execute(
        text(
            """
            SELECT id, item_id, type, qty, deleted
            FROM mouvements_recents
            WHERE IFNULL(deleted, 0) = 0
            """
        )
    ).mappings().all()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# STOCK AJUSTMENTS (régularisation / dépréciation…)
# ---------------------------------------------------------------------------
@router_ajustments.get("/")
def list_stock_ajustments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Any]:
    rows = db.execute(
        text(
            """
            SELECT id, item_id, type, qty, deleted
            FROM stock_ajustments
            WHERE IFNULL(deleted, 0) = 0
            """
        )
    ).mappings().all()
    return [dict(r) for r in rows]
