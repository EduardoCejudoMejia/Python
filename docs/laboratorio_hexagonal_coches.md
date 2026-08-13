# Laboratorio: arquitectura hexagonal con órdenes de coches

El ejemplo está aislado en `src/app/lab_hexagonal_coches` y separa tres capas:

- **Dominio**: `OrdenCoche` contiene las reglas y no importa FastAPI, HTTP ni
  SQLAlchemy.
- **Aplicación**: `CrearOrden` orquesta el caso de uso mediante los puertos
  `RepositorioOrdenes` y `NotificadorOrdenes`, definidos con `Protocol`. El DTO
  `CrearOrdenDTO` transporta la entrada; no es una entidad de dominio.
- **Infraestructura**: adaptadores en memoria, SQLAlchemy y HTTP implementan
  los puertos. La API FastAPI realiza el wiring en el borde.

## Ejecutar pruebas

```bash
poetry run pytest tests/lab_hexagonal_coches
```

La prueba parametrizada de contrato ejecuta las mismas expectativas contra
memoria y SQLAlchemy. El adaptador HTTP usa `httpx.MockTransport`, y la prueba
end-to-end usa FastAPI sin hacer llamadas reales a la red.
