import json
from unittest.mock import Mock

import grpc
import pytest

from app.lab_interop_coches.servicio import (
    Orden,
    PublicadorRabbitMQ,
    crear_cliente,
    crear_servidor,
)
from app.lab_interop_coches.stubs import ordenes_pb2


def test_publicador_rabbitmq_declara_cola_y_publica_json_neutral() -> None:
    canal = Mock()
    publicador = PublicadorRabbitMQ(canal)

    publicador.publicar_orden_creada(Orden("o-1", "Ana", "Yaris", 300_000))

    canal.queue_declare.assert_called_once_with(queue="ordenes.creadas", durable=True)
    cuerpo = canal.basic_publish.call_args.kwargs["body"]
    assert json.loads(cuerpo) == {"orden_id": "o-1", "modelo": "Yaris"}


def test_cliente_y_servidor_grpc_crean_orden_y_publican_evento() -> None:
    publicador = Mock()
    servidor = crear_servidor(publicador)
    puerto = servidor.add_insecure_port("localhost:0")
    servidor.start()
    cliente = crear_cliente(f"localhost:{puerto}")
    try:
        respuesta = cliente.CrearOrden(
            ordenes_pb2.CrearOrdenRequest(
                cliente="Luis", modelo="Versa", precio=350_000
            ),
            timeout=2,
        )
    finally:
        cliente.canal.close()
        servidor.stop(0).wait()

    assert respuesta.cliente == "Luis"
    assert respuesta.modelo == "Versa"
    publicador.publicar_orden_creada.assert_called_once()


def test_grpc_rechaza_orden_invalida() -> None:
    servidor = crear_servidor(Mock())
    puerto = servidor.add_insecure_port("localhost:0")
    servidor.start()
    cliente = crear_cliente(f"localhost:{puerto}")
    try:
        with pytest.raises(grpc.RpcError) as error:
            cliente.CrearOrden(ordenes_pb2.CrearOrdenRequest(cliente="Ana"), timeout=2)
    finally:
        cliente.canal.close()
        servidor.stop(0).wait()

    assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT
