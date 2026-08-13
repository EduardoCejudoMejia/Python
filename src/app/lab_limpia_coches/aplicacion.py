"""Casos de uso, puertos y orquestación de eventos de la aplicación."""

from dataclasses import dataclass
from typing import Protocol

from .entidades import OrdenCoche, OrdenCreada


class RepositorioOrdenes(Protocol):
    def agregar(self, orden: OrdenCoche) -> None: ...

    def obtener(self, orden_id: str) -> OrdenCoche | None: ...


class UnitOfWork(Protocol):
    ordenes: RepositorioOrdenes

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(
        self, exc_type: object, exc_value: object, traceback: object
    ) -> None: ...

    def commit(self) -> None: ...


class Presenter(Protocol):
    def presentar(self, orden: OrdenCoche) -> dict[str, object]: ...


class ManejadorOrdenCreada(Protocol):
    def manejar(self, evento: OrdenCreada) -> None: ...


@dataclass(frozen=True, slots=True)
class CrearOrdenEntrada:
    cliente: str
    modelo: str
    precio: float


class CrearOrden:
    """Caso de uso: controla la transacción, presenta y despacha eventos."""

    def __init__(
        self,
        uow: UnitOfWork,
        presenter: Presenter,
        manejador: ManejadorOrdenCreada,
    ) -> None:
        self._uow = uow
        self._presenter = presenter
        self._manejador = manejador

    def ejecutar(self, entrada: CrearOrdenEntrada) -> dict[str, object]:
        with self._uow:
            orden = OrdenCoche.crear(entrada.cliente, entrada.modelo, entrada.precio)
            self._uow.ordenes.agregar(orden)
            self._uow.commit()

        for evento in orden.eventos:
            self._manejador.manejar(evento)
        return self._presenter.presentar(orden)
