from datetime import datetime
from sqlalchemy import Column, Integer, REAL, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database_online import Base


class MouvementRecent(Base):

    __tablename__ = "mouvements_recents"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id           = Column(Integer,    primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    date        = Column(String(255), nullable=True)
    type        = Column(String(255), nullable=True)
    nature      = Column(String(255), nullable=True)
    raison      = Column(String(255), nullable=True)
    qty         = Column(REAL, nullable=True)
    # =======================================================
    # CLES ETRANGERES
    # =======================================================
    item_id      = Column(Integer, ForeignKey("items.id"),     nullable=False)
    entrepot_id  = Column(Integer, ForeignKey("entrepots.id"), nullable=False)

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
    item     = relationship("Item",     back_populates="mouvements_recents")

    entrepot = relationship("Entrepot", back_populates="mouvements_recents")


class MouvementArchived(Base):

    __tablename__ = "mouvements_archives"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id           = Column(Integer,    primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    date        = Column(String(255), nullable=True)
    type        = Column(String(255), nullable=True)
    nature      = Column(String(255), nullable=True)
    raison      = Column(String(255), nullable=True)
    qty         = Column(REAL, nullable=True)

    # =======================================================
    # CLES ETRANGERES
    # =======================================================
    item_id      = Column(Integer, ForeignKey("items.id"),     nullable=False)
    entrepot_id  = Column(Integer, ForeignKey("entrepots.id"), nullable=False)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced     = Column(Integer,  default=0)
    sync_id    = Column(Integer,  nullable=True)
    deleted    = Column(Integer,  default=0)

    update_at  = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    #  ======================================================= --
    #  RELATION 
    #  ======================================================= --
    item     = relationship("Item",     back_populates="mouvements_archives")

    entrepot = relationship("Entrepot", back_populates="mouvements_archives")

class StockAjustment(Base):

    __tablename__ = "stock_ajustments"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id           = Column(Integer,    primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    date        = Column(String(255), nullable=True)
    type        = Column(String(255), nullable=True)
    nature      = Column(String(255), nullable=True)
    raison      = Column(String(255), nullable=True)
    qty         = Column(REAL, nullable=True)

    # =======================================================
    # CLES ETRANGERES
    # =======================================================
    item_id      = Column(Integer, ForeignKey("items.id"),     nullable=False)
    entrepot_id  = Column(Integer, ForeignKey("entrepots.id"), nullable=False)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced     = Column(Integer,  default=0)
    sync_id    = Column(Integer,  nullable=True)
    deleted    = Column(Integer,  default=0)

    update_at  = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    #  ======================================================= --
    #  RELATION 
    #  ======================================================= --
    item     = relationship("Item",     back_populates="stock_ajustments")
    
    entrepot = relationship("Entrepot", back_populates="stock_ajustments")



