"""Pequeño ejemplo de un dominio desacoplado de su almacenamiento."""

import sqlite3
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Coche:
    """Entidad inmutable: sólo contiene datos y reglas de su identidad."""

    matricula: str
    marca: str
    modelo: str

    def __post_init__(self) -> None:
        if not self.matricula or not self.marca or not self.modelo:
            raise ValueError("Matrícula, marca y modelo son obligatorios.")


class RepositorioCoches(Protocol):
    """Puerto: el servicio conoce esta capacidad, no una base de datos concreta."""

    def guardar(self, coche: Coche) -> None: ...

    def buscar_por_matricula(self, matricula: str) -> Coche | None: ...

    def listar(self) -> list[Coche]: ...


class RepositorioMemoria:
    """Adaptador rápido, útil para pruebas o ejecuciones locales."""

    def __init__(self) -> None:
        self._coches: dict[str, Coche] = {}

    def guardar(self, coche: Coche) -> None:
        if coche.matricula in self._coches:
            raise ValueError("Ya existe un coche con esa matrícula.")
        self._coches[coche.matricula] = coche

    def buscar_por_matricula(self, matricula: str) -> Coche | None:
        return self._coches.get(matricula)

    def listar(self) -> list[Coche]:
        return list(self._coches.values())


class RepositorioSQLite:
    """Adaptador SQL que respeta exactamente el mismo contrato del puerto."""

    def __init__(self, ruta: str = ":memory:") -> None:
        self._conexion = sqlite3.connect(ruta)
        self._conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS coches (
                matricula TEXT PRIMARY KEY,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL
            )
            """
        )

    def guardar(self, coche: Coche) -> None:
        try:
            self._conexion.execute(
                "INSERT INTO coches VALUES (?, ?, ?)",
                (coche.matricula, coche.marca, coche.modelo),
            )
            self._conexion.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError("Ya existe un coche con esa matrícula.") from error

    def buscar_por_matricula(self, matricula: str) -> Coche | None:
        fila = self._conexion.execute(
            "SELECT matricula, marca, modelo FROM coches WHERE matricula = ?",
            (matricula,),
        ).fetchone()
        return Coche(*fila) if fila else None

    def listar(self) -> list[Coche]:
        filas = self._conexion.execute(
            "SELECT matricula, marca, modelo FROM coches ORDER BY matricula"
        ).fetchall()
        return [Coche(*fila) for fila in filas]


class ServicioCoches:
    """SRP: coordina el caso de uso, sin saber dónde se guardan los coches."""

    def __init__(self, repositorio: RepositorioCoches) -> None:
        self._repositorio = repositorio

    def registrar(self, matricula: str, marca: str, modelo: str) -> Coche:
        coche = Coche(matricula, marca, modelo)
        self._repositorio.guardar(coche)
        return coche

    def consultar(self, matricula: str) -> Coche:
        coche = self._repositorio.buscar_por_matricula(matricula)
        if coche is None:
            raise LookupError("Coche no encontrado.")
        return coche

    def inventario(self) -> list[Coche]:
        return self._repositorio.listar()


def crear_repositorio(tipo: str) -> RepositorioCoches:
    """Provider/factory: permite extender adaptadores sin cambiar el servicio."""
    proveedores = {"memoria": RepositorioMemoria, "sqlite": RepositorioSQLite}
    try:
        return proveedores[tipo]()
    except KeyError as error:
        raise ValueError(f"Repositorio desconocido: {tipo}") from error
