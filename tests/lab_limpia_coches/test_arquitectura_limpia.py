import pytest

from app.lab_limpia_coches.aplicacion import CrearOrden, CrearOrdenEntrada
from app.lab_limpia_coches.controlador import crear_orden_controlador
from app.lab_limpia_coches.entidades import OrdenCoche
from app.lab_limpia_coches.infraestructura import (
    PresentadorJSON,
    RegistroEventos,
    UoWMemoria,
)


def test_entidad_crea_evento_de_dominio() -> None:
    orden = OrdenCoche.crear("Ana", "Yaris", 300_000)

    assert orden.eventos[0].orden_id == orden.id
    assert orden.eventos[0].modelo == "Yaris"


def test_entidad_valida_sus_reglas() -> None:
    with pytest.raises(ValueError, match="mayor que cero"):
        OrdenCoche.crear("Ana", "Yaris", 0)


def test_caso_de_uso_confirma_transaccion_y_maneja_evento() -> None:
    uow = UoWMemoria()
    eventos = RegistroEventos()
    caso_uso = CrearOrden(uow, PresentadorJSON(), eventos)

    salida = caso_uso.ejecutar(CrearOrdenEntrada("Luis", "Versa", 350_000))

    assert uow.confirmado is True
    assert uow.ordenes.obtener(str(salida["id"])) is not None
    assert eventos.eventos[0].orden_id == salida["id"]
    assert salida["modelo"] == "Versa"


def test_controlador_orquesta_las_capas_sin_filtrar_entidades() -> None:
    caso_uso = CrearOrden(UoWMemoria(), PresentadorJSON(), RegistroEventos())

    respuesta = crear_orden_controlador(
        {"cliente": "Eva", "modelo": "Ibiza", "precio": 280_000}, caso_uso
    )

    assert set(respuesta) == {"id", "cliente", "modelo", "precio"}
    assert respuesta["cliente"] == "Eva"
