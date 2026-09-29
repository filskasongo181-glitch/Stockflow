# from regex import T
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database_online import Base


class User(Base):

    __tablename__ = "users"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id              = Column(Integer,     primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    name            = Column(String(255), nullable=False)
    first_name      = Column(String(255), nullable=False)
    middle_name     = Column(String(255), nullable=False)
    genre           = Column(String(255), nullable=True)
    email           = Column(String(255), unique=True, nullable=True)
    role            = Column(String(255), nullable=False)
    password        = Column(String(255), nullable=False)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced         = Column(Integer,  nullable=False, default=0)
    sync_id        = Column(Integer,  nullable=False, default=0)
    deleted        = Column(Integer,  nullable=False, default=0)

    update_at      = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at     = Column(DateTime, default=func.now())

    # ---- Relations ----
    audit_logs = relationship("AuditLog", back_populates="user")