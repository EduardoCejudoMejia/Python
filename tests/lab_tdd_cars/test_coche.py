from unittest.mock import Mock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.lab_tdd_cars import Coche


@pytest.fixture
def coche() -> Coche:
    """Estado inicial compartido por las pruebas de ejemplo."""
    return Coche("Toyota", "Yaris", combustible=10)


@pytest.mark.parametrize(
    ("litros", "nivel_esperado"),
    [(1, 11), (15.5, 25.5), (40, 50)],
)
def test_cargar_combustible_actualiza_el_nivel(
    litros: float, nivel_esperado: float
) -> None:
    coche = Coche("Toyota", "Yaris", combustible=10)

    assert coche.cargar_combustible(litros) == nivel_esperado


def test_conducir_reduce_combustible_y_aumenta_kilometraje(coche: Coche) -> None:
    coche.conducir(25)

    assert coche.combustible == 7.5
    assert coche.kilometraje == 25


@pytest.mark.parametrize("combustible", [-1, 51])
def test_no_permite_combustible_inicial_fuera_de_rango(combustible: float) -> None:
    with pytest.raises(ValueError, match="combustible"):
        Coche("Toyota", "Yaris", combustible)


@pytest.mark.parametrize(("marca", "modelo"), [("", "Yaris"), ("Toyota", "")])
def test_marca_y_modelo_son_obligatorios(marca: str, modelo: str) -> None:
    with pytest.raises(ValueError, match="marca y el modelo"):
        Coche(marca, modelo)


@pytest.mark.parametrize("litros", [0, -1, 41])
def test_no_permite_cargas_invalidas_o_superiores_a_la_capacidad(
    coche: Coche, litros: float
) -> None:
    with pytest.raises(ValueError):
        coche.cargar_combustible(litros)


@pytest.mark.parametrize("kilometros", [0, -1, 101])
def test_no_permite_recorridos_invalidos_o_sin_combustible(
    coche: Coche, kilometros: float
) -> None:
    with pytest.raises(ValueError):
        coche.conducir(kilometros)


def test_notifica_la_revision_con_un_mock(coche: Coche) -> None:
    notificador = Mock()
    coche.kilometraje = Coche.KILOMETROS_PARA_REVISION

    assert coche.notificar_revision(notificador) is True
    notificador.enviar.assert_called_once_with("Toyota Yaris necesita revisión.")


def test_no_notifica_si_aun_no_necesita_revision(coche: Coche) -> None:
    notificador = Mock()

    assert coche.notificar_revision(notificador) is False
    notificador.enviar.assert_not_called()


@pytest.mark.propiedades
@given(
    combustible=st.floats(min_value=0.1, max_value=50, allow_nan=False),
    kilometros=st.floats(min_value=0.1, max_value=500, allow_nan=False),
)
def test_propiedad_conducir_conserva_el_balance_de_combustible(
    combustible: float, kilometros: float
) -> None:
    """Para un trayecto posible, lo gastado siempre es km / 10."""
    # El margen evita que un redondeo binario convierta un trayecto límite en inválido.
    kilometros_posibles = min(
        kilometros, combustible * Coche.KILOMETROS_POR_LITRO * 0.99
    )
    coche = Coche("Toyota", "Yaris", combustible)

    coche.conducir(kilometros_posibles)

    assert coche.combustible == pytest.approx(
        combustible - kilometros_posibles / Coche.KILOMETROS_POR_LITRO
    )
    assert coche.kilometraje == pytest.approx(kilometros_posibles)
