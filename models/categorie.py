from sqlalchemy import Column, Integer, LargeBinary, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database_online import Base


class Categorie(Base):

    __tablename__ = "categories"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id              = Column(Integer,     primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    name            = Column(String(100), nullable=False)
    description     = Column(String(255), nullable=True)
    icon            = Column(LargeBinary, nullable=True)  

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
    items          = relationship("Item", back_populates="categorie")