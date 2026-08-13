"""Gateways/adaptadores que implementan los puertos de la aplicación."""

from .entidades import OrdenCoche, OrdenCreada


class RepositorioMemoria:
    def __init__(self) -> None:
        self._ordenes: dict[str, OrdenCoche] = {}

    def agregar(self, orden: OrdenCoche) -> None:
        self._ordenes[orden.id] = orden

    def obtener(self, orden_id: str) -> OrdenCoche | None:
        return self._ordenes.get(orden_id)


class UoWMemoria:
    """UoW de demostración: registra el commit para que sea verificable."""

    def __init__(self, repositorio: RepositorioMemoria | None = None) -> None:
        self.ordenes = repositorio or RepositorioMemoria()
        self.confirmado = False

    def __enter__(self) -> "UoWMemoria":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        if exc_type is not None:
            self.confirmado = False

    def commit(self) -> None:
        self.confirmado = True


class PresentadorJSON:
    def presentar(self, orden: OrdenCoche) -> dict[str, object]:
        return {
            "id": orden.id,
            "cliente": orden.cliente,
            "modelo": orden.modelo,
            "precio": orden.precio,
        }


class RegistroEventos:
    """Manejador de aplicación; en producción puede llamar correo o mensajería."""

    def __init__(self) -> None:
        self.eventos: list[OrdenCreada] = []

    def manejar(self, evento: OrdenCreada) -> None:
        self.eventos.append(evento)
