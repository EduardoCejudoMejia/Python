from unittest.mock import Mock

import pytest

from app.lab_patrones_coches import Coche, ServicioPrecios, crear_estrategia
from app.lab_patrones_coches.precios import (
    AdaptadorProveedorExterno,
    PrecioOferta,
    ProveedorConCache,
)


@pytest.fixture
def coche() -> Coche:
    return Coche("Toyota", "Yaris", 300_000)


@pytest.mark.parametrize(
    ("tipo", "precio_esperado"), [("normal", 300_000), ("oferta", 270_000)]
)
def test_strategy_aplica_la_politica_elegida(
    coche: Coche, tipo: str, precio_esperado: float
) -> None:
    servicio = ServicioPrecios(crear_estrategia(tipo))

    assert servicio.precio_final(coche) == precio_esperado


def test_strategy_permite_otra_politica_sin_cambiar_el_servicio(coche: Coche) -> None:
    servicio = ServicioPrecios(PrecioOferta(descuento=0.25))

    assert servicio.precio_final(coche) == 225_000


def test_decorator_cachea_el_resultado_del_proveedor(coche: Coche) -> None:
    proveedor = Mock()
    proveedor.obtener_precio.return_value = 280_000
    cache = ProveedorConCache(proveedor)

    assert cache.obtener_precio(coche) == 280_000
    assert cache.obtener_precio(coche) == 280_000
    proveedor.obtener_precio.assert_called_once_with(coche)


def test_adapter_traduce_el_contrato_del_proveedor_externo(coche: Coche) -> None:
    externo = Mock()
    externo.consultar.return_value = {"importe": "275000.50"}
    adaptador = AdaptadorProveedorExterno(externo)

    assert adaptador.obtener_precio(coche) == 275_000.50
    externo.consultar.assert_called_once_with("TOYOTA-YARIS")


def test_servicio_combina_adapter_y_cache(coche: Coche) -> None:
    externo = Mock()
    externo.consultar.return_value = {"importe": 280_000}
    proveedor = ProveedorConCache(AdaptadorProveedorExterno(externo))
    servicio = ServicioPrecios(crear_estrategia("normal"), proveedor)

    assert servicio.precio_final(coche) == 280_000
    assert servicio.precio_final(coche) == 280_000
    externo.consultar.assert_called_once()


def test_factory_rechaza_estrategias_desconocidas() -> None:
    with pytest.raises(ValueError, match="desconocida"):
        crear_estrategia("mayoreo")
