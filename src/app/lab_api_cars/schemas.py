"""
Esquemas Pydantic: definen qué datos entran y salen de la API, y los
validan automáticamente (FastAPI usa estos modelos también para generar
la documentación OpenAPI en /docs).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# --------- Coches ---------


class CocheBase(BaseModel):
    marca: str = Field(..., min_length=1, max_length=50, examples=["Toyota"])
    modelo: str = Field(..., min_length=1, max_length=50, examples=["Corolla"])
    anio: int = Field(..., ge=1990, le=2100, examples=[2024])
    precio: float = Field(..., gt=0, examples=[25000.0])
    stock: int = Field(0, ge=0, examples=[5])


class CocheCreate(CocheBase):
    pass


class CocheOut(CocheBase):
    id: int

    model_config = {"from_attributes": True}


# --------- Pedidos ---------


class PedidoBase(BaseModel):
    cliente: str = Field(..., min_length=2, max_length=100, examples=["Ana Pérez"])
    coche_id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0, le=10)


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(BaseModel):
    """Todos los campos son opcionales: solo se actualiza lo que se envía."""

    cantidad: int | None = Field(None, gt=0, le=10)
    estado: Literal["pendiente", "confirmado", "cancelado"] | None = None


class PedidoOut(PedidoBase):
    id: int
    estado: str
    creado_en: datetime

    model_config = {"from_attributes": True}


# --------- Autenticación ---------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
