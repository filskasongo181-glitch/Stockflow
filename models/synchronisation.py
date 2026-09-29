from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database_online import Base


class Synch(Base):

    __tablename__ = "sync_meta"

    #  ======================================================= --
    #  IDENTIFIANT
    #  ======================================================= --
    id              = Column(Integer,     primary_key=True, index=True, autoincrement=True)

    #  ======================================================= --
    #  DONNEES PRINCIPALES
    #  ======================================================= --
    last_sync            = Column(String(100), nullable=False)