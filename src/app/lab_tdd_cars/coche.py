"""Dominio mínimo para practicar pruebas con pytest."""


class Coche:
    """Representa un coche que consume un litro por cada diez kilómetros."""

    CAPACIDAD_DEPOSITO = 50.0
    KILOMETROS_POR_LITRO = 10.0
    KILOMETROS_PARA_REVISION = 10_000

    def __init__(self, marca: str, modelo: str, combustible: float = 0.0) -> None:
        if not marca or not modelo:
            raise ValueError("La marca y el modelo son obligatorios.")
        if not 0 <= combustible <= self.CAPACIDAD_DEPOSITO:
            raise ValueError(
                "El combustible debe estar dentro de la capacidad del depósito."
            )

        self.marca = marca
        self.modelo = modelo
        self.combustible = float(combustible)
        self.kilometraje = 0.0

    def cargar_combustible(self, litros: float) -> float:
        """Carga combustible y devuelve el nivel resultante del depósito."""
        if litros <= 0:
            raise ValueError("Los litros a cargar deben ser mayores que cero.")
        if self.combustible + litros > self.CAPACIDAD_DEPOSITO:
            raise ValueError("La carga supera la capacidad del depósito.")

        self.combustible += litros
        return self.combustible

    def conducir(self, kilometros: float) -> None:
        """Recorre kilómetros si hay combustible suficiente."""
        if kilometros <= 0:
            raise ValueError("Los kilómetros deben ser mayores que cero.")

        combustible_necesario = kilometros / self.KILOMETROS_POR_LITRO
        if combustible_necesario > self.combustible:
            raise ValueError("No hay combustible suficiente para el recorrido.")

        self.combustible -= combustible_necesario
        self.kilometraje += kilometros

    @property
    def necesita_revision(self) -> bool:
        """Indica si ya se alcanzó el kilometraje de mantenimiento."""
        return self.kilometraje >= self.KILOMETROS_PARA_REVISION

    def notificar_revision(self, notificador: object) -> bool:
        """Envía una notificación externa sólo si el coche necesita revisión."""
        if not self.necesita_revision:
            return False

        notificador.enviar(f"{self.marca} {self.modelo} necesita revisión.")
        return True
