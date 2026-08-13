"""Wiring mínimo de FastAPI; el framework queda fuera del caso de uso."""

from fastapi import FastAPI
from pydantic import BaseModel

from .aplicacion import CrearOrden, CrearOrdenDTO
from .infraestructura import RepositorioOrdenesMemoria


class CrearOrdenEntrada(BaseModel):
    cliente: str
    modelo: str
    precio: float


class NotificadorConsola:
    """Adaptador local para ejecutar la API sin depender de una red externa."""

    def notificar_orden_creada(self, orden: object) -> None:
        return None


def crear_app(caso_uso: CrearOrden | None = None) -> FastAPI:
    app = FastAPI(title="Laboratorio hexagonal de coches")
    crear_orden = caso_uso or CrearOrden(
        RepositorioOrdenesMemoria(), NotificadorConsola()
    )

    @app.post("/ordenes", status_code=201)
    def crear_orden_endpoint(entrada: CrearOrdenEntrada) -> dict[str, object]:
        orden = crear_orden.ejecutar(CrearOrdenDTO(**entrada.model_dump()))
        return {"id": orden.id, "modelo": orden.modelo, "precio": orden.precio}

    return app
