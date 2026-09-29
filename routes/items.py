# """
# routes/items.py
# Routes articles — version corrigée (id / sync_id croisés + images)

# Ordre des routes :
#   /sync/... et /media/... AVANT /{item_id}
#   sinon FastAPI traite "sync" comme un item_id.
# """
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from datetime import datetime
# from pydantic import BaseModel
# import os
# import base64
# import binascii
# import hashlib

# from ..database_online import get_db
# from ..models.item import Item
# from ..schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemSync
# from ..routes.auth import get_current_user
# from ..models.user import User

# router = APIRouter()

# ITEM_IMAGES_DIR = os.path.join(
#     os.path.dirname(__file__), "..", "..", "public", "images", "items"
# )
# os.makedirs(ITEM_IMAGES_DIR, exist_ok=True)


# def get_file_sha256(file_path: str) -> Optional[str]:
#     if not file_path or not os.path.isfile(file_path):
#         return None
#     sha256 = hashlib.sha256()
#     try:
#         with open(file_path, "rb") as f:
#             for chunk in iter(lambda: f.read(1024 * 1024), b""):
#                 sha256.update(chunk)
#         return sha256.hexdigest()
#     except OSError:
#         return None


# def get_file_base64(file_path: str) -> Optional[str]:
#     if not file_path or not os.path.isfile(file_path):
#         return None
#     try:
#         with open(file_path, "rb") as f:
#             return base64.b64encode(f.read()).decode("utf-8")
#     except OSError:
#         return None


# def item_to_response(item: Item, with_image: bool = False) -> dict:
#     """Construit un dict compatible ItemResponse."""
#     picture_hash = item.picture_hash
#     picture_data = None
#     if with_image and item.picture_path:
#         picture_file = os.path.join(ITEM_IMAGES_DIR, item.picture_path)
#         if os.path.isfile(picture_file):
#             picture_hash = get_file_sha256(picture_file) or picture_hash
#             picture_data = get_file_base64(picture_file)
#     return {
#         "id": item.id,
#         "sync_id": item.sync_id,
#         "name": item.name,
#         "mark": item.mark,
#         "modele": item.modele,
#         "level": item.level,
#         "qty_by_card": item.qty_by_card,
#         "qty_by_box": item.qty_by_box,
#         "minimal_stock": item.minimal_stock,
#         "length": item.length,
#         "width": item.width,
#         "height": item.height,
#         "purchase_price": item.purchase_price,
#         "sale_price_fc": item.sale_price_fc,
#         "cbm": item.cbm,
#         "sale_price_devise": item.sale_price_devise,
#         "code_barre": item.code_barre,
#         "category_item": item.category_item,
#         "unite_id": item.unite_id,
#         "synced": item.synced,
#         "deleted": item.deleted,
#         "created_at": item.created_at,
#         "update_at": item.update_at,
#         "picture_path": item.picture_path,
#         "picture_hash": picture_hash,
#         "picture_data": picture_data,
#     }


# class PicturePush(BaseModel):
#     """
#     sync_id ici = ID SERVEUR de l'article
#     (côté local : la valeur de local.sync_id)
#     """
#     sync_id: int
#     picture_path: str
#     picture_data: str
#     picture_hash: Optional[str] = None


# # ============================================================
# # SYNCHRONISATION  (avant /{item_id})
# # ============================================================

# @router.get("/sync/changes", response_model=List[ItemResponse])
# def get_changes(
#     since: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     PULL — articles modifiés depuis `since` (YYYY-MM-DD HH:MM:SS).
#     Inclut picture_data (Base64) si le fichier est présent.
#     """
#     try:
#         since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Format attendu : YYYY-MM-DD HH:MM:SS",
#         )

#     items = db.query(Item).filter(Item.update_at >= since_date).all()
#     return [ItemResponse(**item_to_response(it, with_image=True)) for it in items]


# @router.post("/sync/push", response_model=ItemResponse)
# def sync_push(
#     data: ItemSync,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     PUSH métadonnées local → serveur (sans binaire image).

#     Relation croisée :
#       data.sync_id  → ID serveur déjà connu (local.sync_id)
#       data.id       → ID local            (→ server.sync_id)

#     Matching :
#       1) Item.id == data.sync_id          (déjà synchronisé)
#       2) Item.sync_id == data.id          (créé avant, local id connu)
#       3) sinon création
#     """
#     existing = None

#     # 1) local connaît déjà l'id serveur
#     if data.sync_id and data.sync_id != 0:
#         existing = db.query(Item).filter(Item.id == data.sync_id).first()

#     # 2) serveur a déjà enregistré l'id local
#     if existing is None and data.id and data.id != 0:
#         existing = db.query(Item).filter(Item.sync_id == data.id).first()

#     if existing:
#         # Mise à jour si plus récent (ou si pas de date)
#         should_update = True
#         if data.update_at and existing.update_at and data.update_at <= existing.update_at:
#             should_update = False

#         if should_update:
#             update_data = data.model_dump(
#                 exclude={"id", "sync_id"},
#                 exclude_unset=True,
#             )
#             for field, value in update_data.items():
#                 setattr(existing, field, value)
#             # garder le lien croisé
#             if data.id and data.id != 0:
#                 existing.sync_id = data.id
#             existing.synced = 1
#             db.commit()
#             db.refresh(existing)

#         return ItemResponse(**item_to_response(existing, with_image=False))

#     # 3) Création
#     new_item = Item(
#         name=data.name,
#         mark=data.mark,
#         modele=data.modele,
#         level=data.level if data.level is not None else 1,
#         qty_by_card=data.qty_by_card if data.qty_by_card is not None else 0,
#         qty_by_box=data.qty_by_box if data.qty_by_box is not None else 0,
#         minimal_stock=data.minimal_stock if data.minimal_stock is not None else 1,
#         length=data.length,
#         width=data.width,
#         height=data.height,
#         purchase_price=data.purchase_price if data.purchase_price is not None else 1,
#         sale_price_fc=data.sale_price_fc if data.sale_price_fc is not None else 1,
#         unite_id=data.unite_id,
#         cbm=data.cbm if data.cbm is not None else 1,
#         sale_price_devise=data.sale_price_devise if data.sale_price_devise is not None else 1,
#         picture_path=data.picture_path,
#         picture_hash=data.picture_hash,
#         code_barre=data.code_barre,
#         category_item=data.category_item,
#         synced=1,
#         # CROISÉ : server.sync_id = local.id
#         sync_id=(data.id or 0),
#         deleted=data.deleted or 0,
#         created_at=data.created_at,
#         update_at=data.update_at,
#     )
#     db.add(new_item)
#     db.commit()
#     db.refresh(new_item)
#     return ItemResponse(**item_to_response(new_item, with_image=False))


# @router.post("/sync/push/picture")
# def push_item_picture(
#     payload: PicturePush,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     PUSH image seule.
#     payload.sync_id = ID SERVEUR (valeur de local.sync_id).
#     """
#     item = db.query(Item).filter(Item.id == payload.sync_id).first()
#     if not item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Article id={payload.sync_id} introuvable",
#         )

#     client_hash = (payload.picture_hash or "").strip().lower()
#     if not client_hash:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="picture_hash SHA-256 obligatoire",
#         )
#     if len(client_hash) != 64:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="picture_hash doit contenir exactement 64 caractères",
#         )
#     try:
#         int(client_hash, 16)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="picture_hash doit être un SHA-256 hexadécimal valide",
#         )

#     relative_path = payload.picture_path.replace("\\", "/").lstrip("/")
#     if ".." in relative_path.split("/") or not relative_path:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Chemin d'image invalide",
#         )

#     picture_data = payload.picture_data
#     try:
#         if picture_data.startswith("data:") and "," in picture_data:
#             picture_data = picture_data.split(",", 1)[1]
#         image_bytes = base64.b64decode(picture_data, validate=True)
#     except (binascii.Error, ValueError, TypeError) as e:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail=f"picture_data Base64 invalide : {e}",
#         )
#     if not image_bytes:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="L'image décodée est vide",
#         )

#     server_hash = hashlib.sha256(image_bytes).hexdigest().lower()
#     if server_hash != client_hash:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail={
#                 "message": "Le SHA-256 de l'image ne correspond pas au hash envoyé.",
#                 "client_hash": client_hash,
#                 "server_hash": server_hash,
#             },
#         )

#     full_path = os.path.abspath(os.path.join(ITEM_IMAGES_DIR, relative_path))
#     upload_root = os.path.abspath(ITEM_IMAGES_DIR)
#     if not (full_path == upload_root or full_path.startswith(upload_root + os.sep)):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Chemin d'image invalide",
#         )

#     current_hash = (item.picture_hash or "").strip().lower()
#     if current_hash == server_hash and os.path.isfile(full_path):
#         return {
#             "message": "Image déjà synchronisée",
#             "id": item.id,
#             "sync_id": item.sync_id,
#             "picture_path": item.picture_path,
#             "picture_hash": server_hash,
#             "picture_synced": True,
#         }

#     os.makedirs(os.path.dirname(full_path) or ITEM_IMAGES_DIR, exist_ok=True)
#     try:
#         with open(full_path, "wb") as f:
#             f.write(image_bytes)
#     except OSError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Impossible d'enregistrer l'image : {e}",
#         )

#     item.picture_path = relative_path
#     item.picture_hash = server_hash
#     item.synced = 1
#     db.commit()
#     db.refresh(item)

#     return {
#         "message": "Image synchronisée avec succès",
#         "id": item.id,
#         "sync_id": item.sync_id,
#         "picture_path": item.picture_path,
#         "picture_hash": item.picture_hash,
#         "picture_synced": True,
#     }


# # ============================================================
# # MEDIA
# # ============================================================

# @router.get("/media/{file_path:path}")
# def serve_media(file_path: str):
#     """GET /items/media/Nom_Marque_Modele.jpg"""
#     rel = file_path.replace("\\", "/").lstrip("/")
#     if ".." in rel:
#         raise HTTPException(status_code=400, detail="Chemin invalide")
#     full = os.path.join(ITEM_IMAGES_DIR, rel)
#     if not os.path.isfile(full):
#         raise HTTPException(status_code=404, detail="Fichier introuvable")
#     return FileResponse(full)


# # ============================================================
# # CRUD
# # ============================================================

# @router.get("/", response_model=List[ItemResponse])
# def get_all(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     items = db.query(Item).filter(Item.deleted == 0).all()
#     return [ItemResponse(**item_to_response(it)) for it in items]


# @router.get("/categorie/{cat_id}", response_model=List[ItemResponse])
# def get_by_categorie(
#     cat_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     items = (
#         db.query(Item)
#         .filter(Item.category_item == cat_id, Item.deleted == 0)
#         .all()
#     )
#     return [ItemResponse(**item_to_response(it)) for it in items]


# @router.get("/{item_id}", response_model=ItemResponse)
# def get_one(
#     item_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     item = db.query(Item).filter(Item.id == item_id, Item.deleted == 0).first()
#     if not item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Article {item_id} introuvable",
#         )
#     return ItemResponse(**item_to_response(item))


# @router.post("/", response_model=ItemResponse)
# def create(
#     data: ItemCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Création côté web.
#     sync_id = 0 (pas encore de lien local).
#     synced  = 0 → le local le récupérera via /sync/changes.
#     """
#     new_item = Item(
#         name=data.name,
#         mark=data.mark,
#         modele=data.modele,
#         level=data.level if data.level is not None else 1,
#         qty_by_card=data.qty_by_card if data.qty_by_card is not None else 0,
#         qty_by_box=data.qty_by_box if data.qty_by_box is not None else 0,
#         minimal_stock=data.minimal_stock if data.minimal_stock is not None else 1,
#         length=data.length,
#         width=data.width,
#         height=data.height,
#         purchase_price=data.purchase_price if data.purchase_price is not None else 1,
#         sale_price_fc=data.sale_price_fc if data.sale_price_fc is not None else 1,
#         unite_id=data.unite_id,
#         cbm=data.cbm if data.cbm is not None else 1,
#         sale_price_devise=data.sale_price_devise if data.sale_price_devise is not None else 1,
#         picture_path=data.picture_path,
#         picture_hash=data.picture_hash,
#         code_barre=data.code_barre,
#         category_item=data.category_item,
#         synced=0,
#         sync_id=0,
#         deleted=0,
#     )
#     db.add(new_item)
#     db.commit()
#     db.refresh(new_item)
#     return ItemResponse(**item_to_response(new_item))


# @router.put("/{item_id}", response_model=ItemResponse)
# def update(
#     item_id: int,
#     data: ItemUpdate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     item = db.query(Item).filter(Item.id == item_id, Item.deleted == 0).first()
#     if not item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Article {item_id} introuvable",
#         )
#     update_data = data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(item, field, value)
#     # marque non synchronisé pour que le local reçoive le changement
#     item.synced = 0
#     db.commit()
#     db.refresh(item)
#     return ItemResponse(**item_to_response(item))


# @router.delete("/{item_id}")
# def delete(
#     item_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     item = db.query(Item).filter(Item.id == item_id, Item.deleted == 0).first()
#     if not item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Article {item_id} introuvable",
#         )
#     item.deleted = 1
#     item.synced = 0
#     db.commit()
#     return {"message": f"Article {item_id} supprimé"}






























"""
routes/items.py — aligné SyncManager v3 + catégories

Convention payload PUSH métadonnées :
  sync_id   = id LOCAL
  server_id = id MySQL

Convention payload PUSH image :
  sync_id   = id LOCAL   (compat)
  server_id = id MySQL   ← lookup principal
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import os
import base64
import binascii
import hashlib

from database_online import get_db
from models.item import Item
from schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemSync
from routes.auth import get_current_user
from models.user import User

router = APIRouter()

ITEM_IMAGES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "public", "images", "items"
)
os.makedirs(ITEM_IMAGES_DIR, exist_ok=True)


class LinkLocal(BaseModel):
    local_id: int


class PicturePush(BaseModel):
    sync_id: Optional[int] = None      # id LOCAL
    server_id: Optional[int] = None    # id MySQL
    picture_path: str
    picture_data: str
    picture_hash: Optional[str] = None


def get_file_sha256(file_path: str) -> Optional[str]:
    if not file_path or not os.path.isfile(file_path):
        return None
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except OSError:
        return None


def get_file_base64(file_path: str) -> Optional[str]:
    if not file_path or not os.path.isfile(file_path):
        return None
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except OSError:
        return None


def item_to_response(item: Item, with_image: bool = False) -> dict:
    picture_hash = item.picture_hash
    picture_data = None
    if with_image and item.picture_path:
        picture_file = os.path.join(ITEM_IMAGES_DIR, item.picture_path)
        if os.path.isfile(picture_file):
            picture_hash = get_file_sha256(picture_file) or picture_hash
            picture_data = get_file_base64(picture_file)
    return {
        "id": item.id,
        "sync_id": item.sync_id,
        "name": item.name,
        "mark": item.mark,
        "modele": item.modele,
        "level": item.level,
        "qty_by_card": item.qty_by_card,
        "qty_by_box": item.qty_by_box,
        "minimal_stock": item.minimal_stock,
        "length": item.length,
        "width": item.width,
        "height": item.height,
        "purchase_price": item.purchase_price,
        "sale_price_fc": item.sale_price_fc,
        "cbm": item.cbm,
        "sale_price_devise": item.sale_price_devise,
        "code_barre": item.code_barre,
        "category_item": item.category_item,
        "unite_id": item.unite_id,
        "synced": item.synced,
        "deleted": item.deleted,
        "created_at": item.created_at,
        "update_at": item.update_at,
        "picture_path": item.picture_path,
        "picture_hash": picture_hash,
        "picture_data": picture_data,
    }


# ============================================================
# SYNCHRONISATION
# ============================================================

@router.get("/sync/changes", response_model=List[ItemResponse])
def get_changes(
    since: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format attendu : YYYY-MM-DD HH:MM:SS")
    items = db.query(Item).filter(Item.update_at >= since_date).all()
    return [ItemResponse(**item_to_response(it, with_image=True)) for it in items]


@router.post("/sync/push", response_model=ItemResponse)
def sync_push(
    data: ItemSync,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Convention SyncManager :
      data.sync_id   = id LOCAL
      data.server_id = id MySQL
    """
    local_id = int(getattr(data, "sync_id", None) or getattr(data, "id", None) or 0)
    server_id = int(getattr(data, "server_id", None) or 0)
    # compat ancien payload où sync_id = serveur
    if server_id == 0 and getattr(data, "sync_id", None) and getattr(data, "id", None):
        # si les deux sont présents et convention inversée possible : prioriser server_id explicite
        pass

    existing = None
    if server_id > 0:
        existing = db.query(Item).filter(Item.id == server_id).first()
    if existing is None and local_id > 0:
        existing = db.query(Item).filter(Item.sync_id == local_id).first()

    if existing:
        should_update = True
        if data.update_at and existing.update_at and data.update_at <= existing.update_at:
            should_update = False
        if should_update:
            fields = data.model_dump(
                exclude={"id", "sync_id", "server_id", "picture_data"},
                exclude_unset=True,
            )
            for field, value in fields.items():
                if hasattr(existing, field):
                    setattr(existing, field, value)
            if local_id > 0:
                existing.sync_id = local_id
            existing.synced = 1
            db.commit()
            db.refresh(existing)
        return ItemResponse(**item_to_response(existing, with_image=False))

    new_item = Item(
        name=data.name,
        mark=data.mark,
        modele=data.modele,
        level=data.level if data.level is not None else 1,
        qty_by_card=data.qty_by_card if data.qty_by_card is not None else 0,
        qty_by_box=data.qty_by_box if data.qty_by_box is not None else 0,
        minimal_stock=data.minimal_stock if data.minimal_stock is not None else 1,
        length=data.length,
        width=data.width,
        height=data.height,
        purchase_price=data.purchase_price if data.purchase_price is not None else 1,
        sale_price_fc=data.sale_price_fc if data.sale_price_fc is not None else 1,
        unite_id=data.unite_id,
        cbm=data.cbm if data.cbm is not None else 1,
        sale_price_devise=data.sale_price_devise if data.sale_price_devise is not None else 1,
        picture_path=data.picture_path,
        picture_hash=data.picture_hash,
        code_barre=data.code_barre,
        category_item=data.category_item,
        synced=1,
        sync_id=local_id,
        deleted=data.deleted or 0,
        created_at=data.created_at,
        update_at=data.update_at,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return ItemResponse(**item_to_response(new_item, with_image=False))


@router.post("/sync/push/picture")
def push_item_picture(
    payload: PicturePush,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lookup article :
      1) server_id (id MySQL) — prioritaire
      2) sync_id comme id MySQL (compat ancien client)
      3) sync_id comme id local stocké dans Item.sync_id
    """
    item = None
    server_id = int(payload.server_id or 0)
    local_id = int(payload.sync_id or 0)

    if server_id > 0:
        item = db.query(Item).filter(Item.id == server_id).first()
    if item is None and local_id > 0:
        item = db.query(Item).filter(Item.id == local_id).first()
    if item is None and local_id > 0:
        item = db.query(Item).filter(Item.sync_id == local_id).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Article introuvable (server_id={server_id}, sync_id={local_id})",
        )

    client_hash = (payload.picture_hash or "").strip().lower()
    if not client_hash or len(client_hash) != 64:
        raise HTTPException(status_code=422, detail="picture_hash SHA-256 (64 hex) obligatoire")
    try:
        int(client_hash, 16)
    except ValueError:
        raise HTTPException(status_code=422, detail="picture_hash non hexadécimal")

    relative_path = payload.picture_path.replace("\\", "/").lstrip("/")
    # si chemin absolu local a fuité, ne garder que le nom de fichier
    if "/" in relative_path:
        # garder sous-chemin type Nom_Marque_Modele.ext si simple
        parts = [p for p in relative_path.split("/") if p and p != ".."]
        relative_path = parts[-1] if parts else relative_path
    if not relative_path or ".." in relative_path:
        raise HTTPException(status_code=400, detail="Chemin d'image invalide")

    picture_data = payload.picture_data
    try:
        if picture_data.startswith("data:") and "," in picture_data:
            picture_data = picture_data.split(",", 1)[1]
        image_bytes = base64.b64decode(picture_data, validate=True)
    except (binascii.Error, ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"picture_data Base64 invalide : {e}")

    if not image_bytes:
        raise HTTPException(status_code=422, detail="Image vide")

    server_hash = hashlib.sha256(image_bytes).hexdigest().lower()
    if server_hash != client_hash:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "SHA-256 ne correspond pas",
                "client_hash": client_hash,
                "server_hash": server_hash,
            },
        )

    full_path = os.path.abspath(os.path.join(ITEM_IMAGES_DIR, relative_path))
    upload_root = os.path.abspath(ITEM_IMAGES_DIR)
    if not (full_path == upload_root or full_path.startswith(upload_root + os.sep)):
        raise HTTPException(status_code=400, detail="Chemin d'image invalide")

    current_hash = (item.picture_hash or "").strip().lower()
    if current_hash == server_hash and os.path.isfile(full_path):
        return {
            "message": "Image déjà synchronisée",
            "id": item.id,
            "sync_id": item.sync_id,
            "picture_path": item.picture_path,
            "picture_hash": server_hash,
            "picture_synced": True,
        }

    os.makedirs(os.path.dirname(full_path) or ITEM_IMAGES_DIR, exist_ok=True)
    try:
        with open(full_path, "wb") as f:
            f.write(image_bytes)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Impossible d'enregistrer l'image : {e}")

    item.picture_path = relative_path
    item.picture_hash = server_hash
    item.synced = 1
    if local_id > 0 and (not item.sync_id or item.sync_id == 0):
        item.sync_id = local_id
    db.commit()
    db.refresh(item)

    return {
        "message": "Image synchronisée",
        "id": item.id,
        "sync_id": item.sync_id,
        "picture_path": item.picture_path,
        "picture_hash": server_hash,
        "picture_synced": True,
    }


@router.patch("/{item_id}/link", response_model=ItemResponse)
def link_local(
    item_id: int,
    data: LinkLocal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Article {item_id} introuvable")
    item.sync_id = data.local_id
    item.synced = 1
    db.commit()
    db.refresh(item)
    return ItemResponse(**item_to_response(item, with_image=False))


# ============================================================
# CRUD (simplifié — garder tes routes media si besoin)
# ============================================================

@router.get("/", response_model=List[ItemResponse])
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(Item).filter(Item.deleted == 0).all()
    return [ItemResponse(**item_to_response(it)) for it in items]


@router.get("/{item_id}", response_model=ItemResponse)
def get_one(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id, Item.deleted == 0).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Article {item_id} introuvable")
    return ItemResponse(**item_to_response(item))


@router.post("/", response_model=ItemResponse)
def create(
    data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = data.model_dump()
    new_item = Item(**payload, synced=0, sync_id=0, deleted=0)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return ItemResponse(**item_to_response(new_item))


@router.put("/{item_id}", response_model=ItemResponse)
def update(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id, Item.deleted == 0).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Article {item_id} introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item.synced = 0
    db.commit()
    db.refresh(item)
    return ItemResponse(**item_to_response(item))


@router.delete("/{item_id}")
def delete(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == item_id, Item.deleted == 0).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Article {item_id} introuvable")
    item.deleted = 1
    item.synced = 0
    db.commit()
    return {"message": f"Article {item_id} supprimé"}
