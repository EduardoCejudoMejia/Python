"""Modelos de base de datos (SQLAlchemy) del concesionario."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Coche(Base):
    """Catálogo de coches disponibles en el concesionario."""

    __tablename__ = "coches"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    anio = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)

    pedidos = relationship("Pedido", back_populates="coche")


class Pedido(Base):
    """Pedido de compra de uno o varios coches por parte de un cliente."""

    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, nullable=False)
    coche_id = Column(Integer, ForeignKey("coches.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    estado = Column(String, default="pendiente", nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    coche = relationship("Coche", back_populates="pedidos")
