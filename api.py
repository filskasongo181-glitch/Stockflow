"""
# -- ======================================= --
        STOCKFLOW API - POINT D'ENTREE
# -- ======================================= --
"""

# Imports
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

# ============================================
#       CREATION DE L'APPLICATION
# ============================================
app = FastAPI(
    title        = "StockFlow API",
    description  = "API for managing - StockFlow",
    version      = "1.0.0"
)

# ============================================
#      CORS : CORS configuration
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
#     IMPORTS DES MODELES
# ============================================
from  backend.models import user
import backend.database_online as db_online
from .database_online import Base, init_online_engine
# engine, SessionLocal, test_connection

from .models.user            import User
from .models.categorie       import Categorie
from .models.entrepot        import Entrepot
from .models.unite           import Unite
from .models.item            import Item
from .models.audit_log       import AuditLog
from .models.mouvement       import MouvementRecent, MouvementArchived, StockAjustment
from .models.stock           import Stock

# ============================================
#     IMPORTS DES ROUTES
# ============================================
from backend.routes import auth
from backend.routes import users
from backend.routes import categories
from backend.routes import items
from backend.routes import entrepots
from backend.routes import mouvements
from backend.routes import stock_ajustments
from backend.routes import unite
from backend.routes import stock
from backend.routes import audit_log
from backend.routes import consolidation

# ============================================
#     Include API routes
# ============================================
app.include_router(auth.router,             prefix="/auth",              tags=["Authentication"])
app.include_router(users.router,            prefix="/users",             tags=["Utilisateurs"])
app.include_router(categories.router,       prefix="/categories",        tags=["Catégories"])
app.include_router(entrepots.router,        prefix="/entrepots",         tags=["Entrepots"])
app.include_router(unite.router,            prefix="/unites",            tags=["Unités"])
app.include_router(items.router,            prefix="/items",             tags=["Articles"])
app.include_router(mouvements.router,       prefix="/mouvements",        tags=["Mouvements"])
app.include_router(stock_ajustments.router, prefix="/mouvements/ajustements",tags=["Stock Ajustements"])
app.include_router(stock.router,            prefix="/stocks",            tags=["Stocks"])
app.include_router(audit_log.router,        prefix="/logs",              tags=["Audit Logs"])
app.include_router(consolidation.router,     prefix="/consolidation",     tags=["Consolidation"])
# ============================================
#     ROUTE PRINCIPALE
# ============================================
@app.get("/")
def root():

    return {
            "titre"     : "Welcome to StockFlow API!",
            "message"   : "StockFlow API opérationnelle.",
            "version"   : "1.0.0",
            "Status"    : "OK"
            }

# ============================================
#     DEMARRAGE
# ============================================
@app.on_event("startup")
def startup():

    """
    Exécuté au démarrage de l'API.
    1.  Teste la connexion MySQL
    2.  Crée toutes les tables si elles n'existent pas
    3.  Crée l'admin par défault si inexistant
    """
    connected = init_online_engine()

    if connected:
        
        print("Création des tables...")

        Base.metadata.create_all(bind=db_online.engine)

        print("Terminé Ok")

        log.info("Tables vérifiées/créées dans MySQL.")

        create_default_admin()

        log.info("MySQL connection successful - API is ready to serve requests.")
        log.info("MySQL OK - API prete à servir les requêtes.")

    else:

        log.error("MySQL connection failed - API may not function properly.")
        log.error("MySQL non disponible - API en mode dégradé.")


def create_default_admin():
    """
    Crée l'administrateur par défault dans MySQL
    au premier lancement si inexistant.
    Utilise sha256_crupt - pas de limitation de longueur de mot de passe à 72 bytes.
    """   
    import hashlib, os

    if db_online.SessionLocal is None:
        log.error("SessionLocal non initialisé — connexion en ligne inactive.")
        return

    def _hash(password: str) -> str:

        salt = os.urandom(16).hex()

        hashed = hashlib.sha256(
            (salt + password).encode()
        ).hexdigest()

        return f"{salt}${hashed}"

    db : Session = db_online.SessionLocal()

    try:

        """ Vérifier si un admin existe déjà"""
        existing = db.query(User).filter(

            User.email   == "admin@stockflow.com",
            User.deleted == 0

        ).first()

        if not existing:

            # Create default admin user
            admin = User(
                name        =   "Stock",
                first_name  =   "Flow",
                middle_name =   "Managment",
                genre       =   "N/A",
                email       =   "admin@stockflow.com",
                role        =   "Admin",
                password    =   _hash("Admin12345"),
                synced      =   1,
                sync_id     =   0,
                deleted     =   0
            )

            db.add(admin)

            db.commit()

            log.info("Administrateur par défault créé dans MySQL.")

        else:

            log.info("Administrateur déjà existant - rien à faire.")

    except Exception as e:

        log.error(f"Erreur création admin : {e}")

        db.rollback()

    finally:

        db.close()

# ============================================
#     LANCEMENT
# ============================================
if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.api:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True
    )

