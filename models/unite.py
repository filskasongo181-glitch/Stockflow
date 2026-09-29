from sqlalchemy import Column, Integer, Text, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_online import Base


class Unite(Base):

    __tablename__ = "unites"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id                  = Column(Integer,     primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    niveau_3            = Column(String(255), nullable=True)
    niveau_2            = Column(String(255), nullable=True)
    niveau_1            = Column(String(255), nullable=True)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced              = Column(Integer,  default=0)
    sync_id             = Column(Integer,  nullable=True)
    deleted             = Column(Integer,  default=0)

    update_at           = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at          = Column(DateTime, default=func.now())

    #  ======================================================= --
    #  RELATION 
    #  ======================================================= --
    items = relationship("Item", back_populates="unite")