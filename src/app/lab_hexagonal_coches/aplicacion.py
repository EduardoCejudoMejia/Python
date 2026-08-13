"""Capa de aplicación: puertos, DTO y orquestación del caso de uso."""

from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from .dominio import OrdenCoche


class RepositorioOrdenes(Protocol):
    def guardar(self, orden: OrdenCoche) -> None: ...

    def buscar_por_id(self, id_orden: str) -> OrdenCoche | None: ...


class NotificadorOrdenes(Protocol):
    def notificar_orden_creada(self, orden: OrdenCoche) -> None: ...


@dataclass(frozen=True, slots=True)
class CrearOrdenDTO:
    cliente: str
    modelo: str
    precio: float


class CrearOrden:
    """Caso de uso que depende exclusivamente de puertos estables."""

    def __init__(
        self, repositorio: RepositorioOrdenes, notificador: NotificadorOrdenes
    ) -> None:
        self._repositorio = repositorio
        self._notificador = notificador

    def ejecutar(self, datos: CrearOrdenDTO) -> OrdenCoche:
        orden = OrdenCoche(
            id=str(uuid4()),
            cliente=datos.cliente,
            modelo=datos.modelo,
            precio=datos.precio,
        )
        self._repositorio.guardar(orden)
        self._notificador.notificar_orden_creada(orden)
        return orden
