"""Servicio gRPC y adaptador RabbitMQ para órdenes de coches."""

import json
from concurrent import futures
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

import grpc
import pika

from .stubs import ordenes_pb2, ordenes_pb2_grpc


@dataclass(frozen=True, slots=True)
class Orden:
    id: str
    cliente: str
    modelo: str
    precio: float


class PublicadorEventos(Protocol):
    def publicar_orden_creada(self, orden: Orden) -> None: ...


class PublicadorRabbitMQ:
    """Publica el evento como JSON para consumidores de cualquier lenguaje."""

    def __init__(self, canal: object, cola: str = "ordenes.creadas") -> None:
        self._canal = canal
        self._cola = cola
        self._canal.queue_declare(queue=cola, durable=True)

    def publicar_orden_creada(self, orden: Orden) -> None:
        cuerpo = json.dumps({"orden_id": orden.id, "modelo": orden.modelo})
        propiedades = pika.BasicProperties(content_type="application/json")
        self._canal.basic_publish(
            exchange="",
            routing_key=self._cola,
            body=cuerpo.encode(),
            properties=propiedades,
        )


class ServicioOrdenes(ordenes_pb2_grpc.OrdenesServiceServicer):
    def __init__(self, publicador: PublicadorEventos) -> None:
        self._publicador = publicador

    def CrearOrden(
        self,
        request: ordenes_pb2.CrearOrdenRequest,
        context: grpc.ServicerContext,
    ) -> ordenes_pb2.OrdenResponse:
        if not request.cliente or not request.modelo or request.precio <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Datos de orden inválidos.")

        orden = Orden(str(uuid4()), request.cliente, request.modelo, request.precio)
        self._publicador.publicar_orden_creada(orden)
        return ordenes_pb2.OrdenResponse(
            id=orden.id,
            cliente=orden.cliente,
            modelo=orden.modelo,
            precio=orden.precio,
        )


def crear_servidor(publicador: PublicadorEventos) -> grpc.Server:
    """Crea un servidor sin iniciarlo, para permitir configuración externa."""
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    ordenes_pb2_grpc.add_OrdenesServiceServicer_to_server(
        ServicioOrdenes(publicador), servidor
    )
    return servidor


def crear_cliente(direccion: str) -> ordenes_pb2_grpc.OrdenesServiceStub:
    """Cliente mínimo; el canal se asocia al stub para poder cerrarlo luego."""
    canal = grpc.insecure_channel(direccion)
    cliente = ordenes_pb2_grpc.OrdenesServiceStub(canal)
    cliente.canal = canal
    return cliente
