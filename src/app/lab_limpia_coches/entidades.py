"""Capa de entidades: reglas de negocio sin dependencias externas."""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class OrdenCreada:
    orden_id: str
    modelo: str


@dataclass(slots=True)
class OrdenCoche:
    cliente: str
    modelo: str
    precio: float
    id: str = field(default_factory=lambda: str(uuid4()))
    eventos: list[OrdenCreada] = field(default_factory=list)

    @classmethod
    def crear(cls, cliente: str, modelo: str, precio: float) -> "OrdenCoche":
        if not cliente or not modelo:
            raise ValueError("Cliente y modelo son obligatorios.")
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")

        orden = cls(cliente=cliente, modelo=modelo, precio=precio)
        orden.eventos.append(OrdenCreada(orden.id, orden.modelo))
        return orden
