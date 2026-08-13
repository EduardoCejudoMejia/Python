"""Strategy, Decorator y Adapter aplicados a la consulta de precios de coches."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Coche:
    marca: str
    modelo: str
    precio_base: float


class EstrategiaPrecio(Protocol):
    """Strategy: permite añadir políticas de precio sin cambiar el servicio."""

    def calcular(self, coche: Coche) -> float: ...


class PrecioNormal:
    def calcular(self, coche: Coche) -> float:
        return coche.precio_base


class PrecioOferta:
    def __init__(self, descuento: float = 0.10) -> None:
        self._descuento = descuento

    def calcular(self, coche: Coche) -> float:
        return coche.precio_base * (1 - self._descuento)


class ProveedorPrecios(Protocol):
    """Contrato que necesita el servicio, independiente de la API externa."""

    def obtener_precio(self, coche: Coche) -> float: ...


class AdaptadorProveedorExterno:
    """Adapter: traduce la API ajena ``consultar(codigo)`` a nuestro contrato."""

    def __init__(self, proveedor_externo: object) -> None:
        self._proveedor_externo = proveedor_externo

    def obtener_precio(self, coche: Coche) -> float:
        codigo = f"{coche.marca}-{coche.modelo}".upper()
        respuesta = self._proveedor_externo.consultar(codigo)
        return float(respuesta["importe"])


class ProveedorConCache:
    """Decorator: conserva el contrato y evita consultas repetidas al proveedor."""

    def __init__(self, proveedor: ProveedorPrecios) -> None:
        self._proveedor = proveedor
        self._cache: dict[Coche, float] = {}

    def obtener_precio(self, coche: Coche) -> float:
        if coche not in self._cache:
            self._cache[coche] = self._proveedor.obtener_precio(coche)
        return self._cache[coche]


class ServicioPrecios:
    """Facade pequeña que combina la política de precio y el proveedor elegido."""

    def __init__(
        self, estrategia: EstrategiaPrecio, proveedor: ProveedorPrecios | None = None
    ) -> None:
        self._estrategia = estrategia
        self._proveedor = proveedor

    def precio_final(self, coche: Coche) -> float:
        precio = (
            self._proveedor.obtener_precio(coche)
            if self._proveedor is not None
            else self._estrategia.calcular(coche)
        )
        return round(precio, 2)


def crear_estrategia(tipo: str) -> EstrategiaPrecio:
    """Factory: centraliza la construcción de las estrategias disponibles."""
    estrategias = {"normal": PrecioNormal, "oferta": PrecioOferta}
    try:
        return estrategias[tipo]()
    except KeyError as error:
        raise ValueError(f"Estrategia desconocida: {tipo}") from error
