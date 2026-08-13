"""Adaptadores de infraestructura intercambiables para los puertos."""

import httpx
from sqlalchemy import Float, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .dominio import OrdenCoche


class Base(DeclarativeBase):
    pass


class OrdenModelo(Base):
    __tablename__ = "ordenes_coche"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    cliente: Mapped[str] = mapped_column(String)
    modelo: Mapped[str] = mapped_column(String)
    precio: Mapped[float] = mapped_column(Float)


class RepositorioOrdenesMemoria:
    def __init__(self) -> None:
        self._ordenes: dict[str, OrdenCoche] = {}

    def guardar(self, orden: OrdenCoche) -> None:
        self._ordenes[orden.id] = orden

    def buscar_por_id(self, id_orden: str) -> OrdenCoche | None:
        return self._ordenes.get(id_orden)


class RepositorioOrdenesSQLAlchemy:
    """Adaptador SQL: la entidad de SQLAlchemy no sale de esta capa."""

    def __init__(self, sesion: sessionmaker[Session]) -> None:
        self._sesion = sesion

    def guardar(self, orden: OrdenCoche) -> None:
        with self._sesion() as sesion:
            sesion.add(
                OrdenModelo(
                    id=orden.id,
                    cliente=orden.cliente,
                    modelo=orden.modelo,
                    precio=orden.precio,
                )
            )
            sesion.commit()

    def buscar_por_id(self, id_orden: str) -> OrdenCoche | None:
        with self._sesion() as sesion:
            consulta = select(OrdenModelo).where(OrdenModelo.id == id_orden)
            modelo = sesion.scalar(consulta)
            if modelo is None:
                return None
            return OrdenCoche(modelo.id, modelo.cliente, modelo.modelo, modelo.precio)


class NotificadorHTTP:
    """Adaptador HTTP: concentra el formato de la integración externa."""

    def __init__(self, url: str, cliente: httpx.Client | None = None) -> None:
        self._url = url
        self._cliente = cliente or httpx.Client()

    def notificar_orden_creada(self, orden: OrdenCoche) -> None:
        respuesta = self._cliente.post(
            self._url,
            json={
                "orden_id": orden.id,
                "modelo": orden.modelo,
                "evento": "orden_creada",
            },
        )
        respuesta.raise_for_status()


def crear_repositorio_sqlite(ruta: str = ":memory:") -> RepositorioOrdenesSQLAlchemy:
    """Composition root de infraestructura para usar SQLite en desarrollo."""
    motor = create_engine(f"sqlite:///{ruta}")
    Base.metadata.create_all(motor)
    return RepositorioOrdenesSQLAlchemy(sessionmaker(motor))


def respuesta_notificacion(request: httpx.Request) -> httpx.Response:
    """Helper para simular la API HTTP desde pruebas o demostraciones."""
    return httpx.Response(202)
