import hashlib

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    
    return hash_password(password) == hashed