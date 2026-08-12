import pytest

from app.lab_solid_coches import Coche, ServicioCoches, crear_repositorio
from app.lab_solid_coches.servicio import (
    RepositorioCoches,
    RepositorioMemoria,
    RepositorioSQLite,
)


@pytest.fixture(params=[RepositorioMemoria, RepositorioSQLite])
def repositorio(request: pytest.FixtureRequest) -> RepositorioCoches:
    """Misma batería para los adaptadores: verificación práctica de LSP."""
    return request.param()


def test_los_adaptadores_cumplen_el_puerto(repositorio: RepositorioCoches) -> None:
    repositorio.guardar(Coche("ABC-123", "Toyota", "Yaris"))

    assert repositorio.buscar_por_matricula("ABC-123") == Coche(
        "ABC-123", "Toyota", "Yaris"
    )
    assert repositorio.listar() == [Coche("ABC-123", "Toyota", "Yaris")]


def test_los_adaptadores_rechazan_matriculas_duplicadas(
    repositorio: RepositorioCoches,
) -> None:
    coche = Coche("ABC-123", "Toyota", "Yaris")
    repositorio.guardar(coche)

    with pytest.raises(ValueError, match="Ya existe"):
        repositorio.guardar(coche)


def test_servicio_depende_del_puerto_y_no_del_adaptador_concreto() -> None:
    servicio = ServicioCoches(RepositorioMemoria())

    coche = servicio.registrar("XYZ-456", "Nissan", "Versa")

    assert coche == servicio.consultar("XYZ-456")


def test_servicio_reporta_coche_inexistente() -> None:
    servicio = ServicioCoches(RepositorioMemoria())

    with pytest.raises(LookupError, match="no encontrado"):
        servicio.consultar("SIN-000")


@pytest.mark.parametrize("tipo", ["memoria", "sqlite"])
def test_factory_provee_un_repositorio_intercambiable(tipo: str) -> None:
    servicio = ServicioCoches(crear_repositorio(tipo))

    servicio.registrar("SOL-001", "SEAT", "Ibiza")

    assert servicio.inventario() == [Coche("SOL-001", "SEAT", "Ibiza")]


def test_factory_rechaza_un_proveedor_desconocido() -> None:
    with pytest.raises(ValueError, match="desconocido"):
        crear_repositorio("redis")
