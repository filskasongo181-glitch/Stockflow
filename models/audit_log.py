from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database_online import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id              = Column(Integer,     primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  CLE ETRANGER
    #  ======================================================= --
    user_id         =   Column(Integer, ForeignKey("users.id"), nullable=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    action          = Column(String(255), nullable=False)
    details         = Column(String(255), nullable=True)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced         = Column(Integer,  nullable=False, default=0)
    sync_id        = Column(Integer,  nullable=False, default=0)
    deleted        = Column(Integer,  nullable=False, default=0)

    update_at      = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at     = Column(DateTime, default=func.now())

    #  ======================================================= --
    #  RELATION 
    #  ======================================================= --
    user = relationship("User", back_populates="audit_logs")

