"""Controlador de borde: traduce un diccionario de entrada al caso de uso."""

from .aplicacion import CrearOrden, CrearOrdenEntrada


def crear_orden_controlador(
    cuerpo: dict[str, object], caso_uso: CrearOrden
) -> dict[str, object]:
    entrada = CrearOrdenEntrada(
        cliente=str(cuerpo["cliente"]),
        modelo=str(cuerpo["modelo"]),
        precio=float(cuerpo["precio"]),
    )
    return caso_uso.ejecutar(entrada)
