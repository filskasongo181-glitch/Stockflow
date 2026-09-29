from sqlalchemy import Column, Integer, String, REAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_online import Base

class Item(Base):

    __tablename__ = "items"

    # =======================================================
    # IDENTIFIANT
    # =======================================================
    id                  = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # =======================================================
    # CLES ETRANGERES
    # =======================================================
    category_item       = Column(Integer, ForeignKey("categories.id"), nullable= True)
    unite_id            = Column(Integer, ForeignKey("unites.id"), nullable= True)

    # =======================================================
    # DONNEES PRINCIPALES
    # =======================================================
    name              = Column(String(255),    nullable=False)
    mark              = Column(String(255),    nullable=True)
    modele            = Column(String(255),    nullable=True)
    level             = Column(Integer, default=1)
    qty_by_card       = Column(Integer, default=0)
    qty_by_box        = Column(Integer, default=0)
    minimal_stock     = Column(Integer, default=1)
    length            = Column(REAL,    nullable=True)
    width             = Column(REAL,    nullable=True)
    height            = Column(REAL,    nullable=True)
    purchase_price    = Column(REAL,    default=1)
    sale_price_fc     = Column(REAL,    default=1)
    cbm               = Column(REAL,    default=1)
    sale_price_devise = Column(REAL,    default=1)
    picture_path      = Column(String(500),    nullable=True)
    picture_hash      = Column(String(500),    nullable=True)
    code_barre        = Column(String(255),    nullable=True)

    #  ======================================================= --
    #  SYNCHRONISATION 
    #  ======================================================= --
    synced              = Column(Integer,  nullable=False, default=0)
    sync_id             = Column(Integer,  nullable=False, default=0)
    deleted             = Column(Integer,  nullable=False, default=0)

    update_at           = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at          = Column(DateTime, default=func.now())

    #  ======================================================= --
    #  RELATION 
    #  ======================================================= --

    categorie            = relationship("Categorie",        back_populates="items")

    stocks              = relationship("Stock", back_populates="item")

    mouvements_recents   = relationship("MouvementRecent",  back_populates="item")

    mouvements_archives  = relationship("MouvementArchived",back_populates="item")

    stock_ajustments     = relationship("StockAjustment",   back_populates="item")

    unite               = relationship("Unite",            back_populates="items")