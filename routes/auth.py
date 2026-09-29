"""
# =========================================== #
#     AUTHENTIFICATION — AUTH ROUTES          #
# =========================================== #
"""
import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from backend.database_online import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin, UserResponse, Token



log = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
router = APIRouter()

# SECRET_KEY   = os.getenv("SECRET_KEY", "stockflow_secret_key_2026")
SECRET_KEY   = os.getenv("SECRET_KEY")

print("SECRET_KEY chargée :", bool(SECRET_KEY))
print("SECRET_KEY longueur :", len(SECRET_KEY) if SECRET_KEY else 0)

ALGORITHM    = "HS256"

TOKEN_EXPIRE = 60 * 24  # 24 heures en minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================
def hash_password(password: str) -> str:

    """Hash un mot de passe avec SHA-256 + sel aléatoire."""
    salt = os.urandom(16).hex()

    hashed = hashlib.sha256(
        (salt + password).encode()
    ).hexdigest()

    return f"{salt}${hashed}"

def verify_password(password: str, stored: str) -> bool:

    """Vérifie un mot de passe contre son hash."""
    try:

        print("Password reçu :", password)
        print("Stored :", stored)

        salt, hashed = stored.split("$")

        candidate = hashlib.sha256(
            (salt + password).encode()
        ).hexdigest()

        print("Candidate :", candidate)
        print("Stored hash :", hashed)
        print(candidate == hashed)

        return candidate == hashed
    
    except Exception as e :
        log.error(f"Erreur vérification : {e}")

        return False

def create_token(data: dict) -> str:

    """
    Crée un token JWT.
    data contient l'email de l'utilisateur.
    """
    to_encode = data.copy()

    expire    = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:

    """
    Vérifie un token JWT et retourne l'email.
    Lève une exception si le token est invalide ou expiré.
    """
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email   = payload.get("sub")

        if email is None:

            raise HTTPException(

                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"

            )
        
        return email
    
    except JWTError:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"

        )
    
def get_current_user(
        
    token : str     = Depends(oauth2_scheme),
    db    : Session = Depends(get_db)

    ) -> User:

    """
    Dépendance réutilisable dans toutes les routes protégées.
    Vérifie le token et retourne l'utilisateur connecté.

    """
    email = verify_token(token)

    user = db.query(User).filter(
        User.email   == email,
        User.deleted == 0

    ).first()

    if not user:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable"

        )
    
    return user

# ============================================================
# ROUTES
# ============================================================
@router.post("/register", response_model=UserResponse)
def register(

    user_data   : UserCreate, 
    db          : Session = Depends(get_db)
    
    ):

    """
    Crée un nouvel utilisateur.
    """

    # Vérifier si l'email existe déjà
    existing = db.query(User).filter(

        User.email == user_data.email

    ).first()

    if existing:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Créer l'utilisateur avec mot de passe hashé
    new_user = User(
        name             = user_data.name,
        first_name       = user_data.first_name,
        middle_name       = user_data.middle_name,
        genre            = user_data.genre,
        email            = user_data.email,
        role             = user_data.role,
        password         = hash_password(user_data.password),
        synced           = 1,
        sync_id          = 0,
        deleted          = 0
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(

    credentials     : UserLogin, 
    db              : Session = Depends(get_db)
    
    ):

    """
    Connexion d'un utilisateur.
    Retourne un token JWT si les identifiants sont corrects.
    """

    # Chercher l'utilisateur par email
    user = db.query(User).filter(

        User.email      == credentials.email,
        User.deleted    == 0

    ).first()

    # Message générique pour la sécurité
    if not user :

        logging.warning(f"Login échoué - email inconnu : {credentials.email}")

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"

        )
    
    if not verify_password(credentials.password, user.password):

        logging.warning(f"Login échoué - mot de passe incorrect pour : {credentials.email}")

        print("====================")
        print("Email :", credentials.email)
        print("Mot de passe saisi :", credentials.password)
        print("Hash enregistré :", user.password)
        print("====================")

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"

        )
    
    # Créer le token
    token = create_token({"sub": user.email})

    log.info(f"Utilisateur connecté : {user.email} (Role: {user.role})")
    log.info(f"Login réussi : {credentials.email}")

    return {
        "access_token" : token,
        "token_type"   : "bearer",
        "user"         : user
    }
@router.get("/me", response_model=UserResponse)
def get_me(
    
    current_user: User = Depends(get_current_user)
    
    ):

    """
    Retourne les infos de l'utilisateur connecté.
    """

    return current_user

@router.post("/logout")
def logout():

    """
    Déconnexion — le navigateur supprime le token de son côté.
    """
    return {"message": "Déconnexion réussie"}

