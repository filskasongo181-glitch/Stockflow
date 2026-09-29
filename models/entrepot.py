from sqlalchemy import Column, Integer, Text, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_online import Base


class Entrepot(Base):

    __tablename__ = "entrepots"


    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id              = Column(Integer,     primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    reference       = Column(String(255),    nullable=False)
    description     = Column(String(255),    nullable=True)
    localisation    = Column(String(255),    nullable=True)
    capacity        = Column(Integer, nullable=True)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced          = Column(Integer,  nullable=False, default=0)
    sync_id         = Column(Integer,  nullable=False, default=0)
    deleted         = Column(Integer,  nullable=False, default=0)


    update_at       = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at      = Column(DateTime, default=func.now())

    #  ======================================================= --
    #  RELATION 
    #  ======================================================= --

    mouvements_recents   = relationship("MouvementRecent",   back_populates="entrepot")

    mouvements_archives  = relationship("MouvementArchived", back_populates="entrepot")

    stock_ajustments     = relationship("StockAjustment",    back_populates="entrepot")

    stocks               = relationship("Stock",             back_populates="entrepot")