import json
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.lab_hexagonal_coches.api import crear_app
from app.lab_hexagonal_coches.aplicacion import (
    CrearOrden,
    CrearOrdenDTO,
    RepositorioOrdenes,
)
from app.lab_hexagonal_coches.dominio import OrdenCoche
from app.lab_hexagonal_coches.infraestructura import (
    Base,
    NotificadorHTTP,
    RepositorioOrdenesMemoria,
    RepositorioOrdenesSQLAlchemy,
)


@pytest.fixture(params=["memoria", "sql"])
def repositorio(request: pytest.FixtureRequest) -> RepositorioOrdenes:
    """Contrato: ambos adaptadores deben almacenar y recuperar igual."""
    if request.param == "memoria":
        return RepositorioOrdenesMemoria()
    motor = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(motor)
    return RepositorioOrdenesSQLAlchemy(sessionmaker(motor))


def test_dominio_rechaza_precio_invalido() -> None:
    with pytest.raises(ValueError, match="mayor que cero"):
        OrdenCoche("1", "Ana", "Yaris", 0)


def test_contrato_de_repositorios(repositorio: RepositorioOrdenes) -> None:
    orden = OrdenCoche("orden-1", "Ana", "Yaris", 300_000)
    repositorio.guardar(orden)

    assert repositorio.buscar_por_id("orden-1") == orden
    assert repositorio.buscar_por_id("ausente") is None


def test_caso_de_uso_guarda_y_notifica(repositorio: RepositorioOrdenes) -> None:
    notificador = Mock()
    caso_uso = CrearOrden(repositorio, notificador)

    orden = caso_uso.ejecutar(CrearOrdenDTO("Luis", "Versa", 350_000))

    assert repositorio.buscar_por_id(orden.id) == orden
    notificador.notificar_orden_creada.assert_called_once_with(orden)


def test_adaptador_http_traduce_la_notificacion() -> None:
    solicitudes: list[httpx.Request] = []

    def responder(request: httpx.Request) -> httpx.Response:
        solicitudes.append(request)
        return httpx.Response(202)

    with httpx.Client(transport=httpx.MockTransport(responder)) as cliente:
        notificador = NotificadorHTTP("https://notificaciones.test/eventos", cliente)
        notificador.notificar_orden_creada(
            OrdenCoche("orden-2", "Eva", "Ibiza", 280_000)
        )

    assert json.loads(solicitudes[0].content) == {
        "orden_id": "orden-2",
        "modelo": "Ibiza",
        "evento": "orden_creada",
    }


def test_end_to_end_con_fastapi_y_adaptadores_en_memoria() -> None:
    cliente = TestClient(crear_app())

    respuesta = cliente.post(
        "/ordenes", json={"cliente": "Ana", "modelo": "Yaris", "precio": 300_000}
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["modelo"] == "Yaris"
    assert respuesta.json()["precio"] == 300_000
