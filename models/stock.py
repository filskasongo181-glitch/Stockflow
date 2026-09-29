from sqlalchemy import Column, Integer, ForeignKey, REAL, Float, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_online import Base


class Stock(Base):

    __tablename__ = "stocks"

    # ======================================================= --
    # IDENTIFIANT
    # ======================================================= --
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ======================================================= --
    # CLES ETRANGERES
    # ======================================================= --
    item_id     = Column(Integer, ForeignKey("items.id"), nullable=False )
    entrepot_id = Column(Integer, ForeignKey("entrepots.id"), default=1)

    # ======================================================= --
    # DONNEES PRINCIPALES
    # ======================================================= --
    stock_actual = Column(REAL, nullable=True)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced     = Column(Integer,  default=0)
    sync_id    = Column(Integer,  nullable=True)
    deleted    = Column(Integer,  default=0)

    update_at  = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    # ======================================================= --
    # RELATIONS
    # ======================================================= --

    item = relationship("Item",back_populates="stocks")

    entrepot = relationship("Entrepot",back_populates="stocks")