# Laboratorio: interoperabilidad con órdenes de coches

El contrato neutral está en `src/app/lab_interop_coches/proto/ordenes.proto`.
Protobuf permite que un cliente Java, Go o Python use el mismo servicio gRPC.
Para regenerar los stubs tras cambiar el contrato:

```bash
poetry run python -m grpc_tools.protoc \
  -I src/app/lab_interop_coches/proto \
  --python_out=src/app/lab_interop_coches/stubs \
  --grpc_python_out=src/app/lab_interop_coches/stubs \
  src/app/lab_interop_coches/proto/ordenes.proto
```

`ServicioOrdenes` crea una orden por gRPC y publica `OrderCreated` mediante el
adaptador RabbitMQ. El evento se serializa como JSON, una decisión deliberada
para consumidores heterogéneos. Para usar RabbitMQ real se crearía una conexión
`pika.BlockingConnection`, se obtendría su canal y se inyectaría en
`PublicadorRabbitMQ`.

## Ejecutar

```bash
poetry run pytest tests/lab_interop_coches
```

Las pruebas levantan gRPC en un puerto local efímero y simulan RabbitMQ, sin
requerir un servicio externo.
