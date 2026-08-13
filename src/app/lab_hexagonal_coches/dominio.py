"""Capa de dominio: reglas de negocio sin dependencias de infraestructura."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OrdenCoche:
    id: str
    cliente: str
    modelo: str
    precio: float

    def __post_init__(self) -> None:
        if not self.id or not self.cliente or not self.modelo:
            raise ValueError("Id, cliente y modelo son obligatorios.")
        if self.precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
