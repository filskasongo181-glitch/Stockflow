from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
CA_FILE  = BASE_DIR / "Certs" / "Ca.pem"
load_dotenv(BASE_DIR / ".env")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
# =========================================================
# ENGINE — créé mais PAS connecté immédiatement
# =========================================================
engine = None
SessionLocal = None
Base = declarative_base()

def init_online_engine():
    """
    Initialise la connexion en ligne.
    Appelé UNIQUEMENT si internet est disponible.
    Retourne True si succès, False sinon.
    """
    global engine, SessionLocal

    try:

        connect_args = {}

        if CA_FILE.exists():
            connect_args["ssl"] = {"ca": str(CA_FILE)}
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args=connect_args,
            # Timeout court pour ne pas bloquer l'UI
            pool_timeout=5,
        )
        # Test réel de connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        print("✅ Connexion en ligne établie.")

        return True
    
    except Exception as e:
        print(f"Erreur lors de l'initialisation du moteur en ligne : {e}")
        print(f"⚠️ Connexion en ligne impossible : {e}")
        engine      = None
        SessionLocal = None
        return False
def get_db():
    """Générateur de session pour les routes API."""
    if SessionLocal is None:
        raise RuntimeError("SessionLocal non initialisé — connexion en ligne inactive.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def test_connection():
    """Test rapide de connexion — affiche toujours la cause."""
    global engine, SessionLocal
    print("=== TEST MYSQL ===")
    print("DB_HOST:", DB_HOST)
    print("DB_PORT:", DB_PORT)
    print("DB_NAME:", DB_NAME)
    print("DB_USER:", DB_USER)
    print("PASSWORD défini:", bool(DB_PASSWORD))
    print("CA_FILE:", CA_FILE, "existe:", CA_FILE.exists())
    try:
        connect_args = {}
        if CA_FILE.exists():
            connect_args["ssl"] = {"ca": str(CA_FILE)}
        else:
            # TiDB Cloud exige souvent SSL même sans fichier CA local
            connect_args["ssl"] = {"ssl": True}
        test_engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            connect_args=connect_args,
            pool_timeout=5,
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        # Si OK, on enregistre l'engine global
        engine = test_engine
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
        print("Connexion MySQL OK")
        return True
    except Exception as e:
        print("ERREUR MYSQL DETAIL:", type(e).__name__, e)
        engine = None
        SessionLocal = None
        return False
