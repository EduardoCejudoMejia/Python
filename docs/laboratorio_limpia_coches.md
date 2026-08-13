# Laboratorio: arquitectura limpia con órdenes de coches

El laboratorio aislado `src/app/lab_limpia_coches` organiza las dependencias
hacia adentro:

- `entidades.py`: `OrdenCoche` y el evento de dominio `OrdenCreada`.
- `aplicacion.py`: caso de uso `CrearOrden`, DTOs y puertos `Protocol`.
- `infraestructura.py`: repositorio, Unit of Work, presenter y manejador en
  memoria; estos detalles dependen de las capas internas, no al revés.
- `controlador.py`: adapta una entrada de borde a un DTO y devuelve la salida
  preparada por el presenter, sin exponer la entidad.

El Unit of Work define el límite transaccional: primero se guarda y confirma la
orden; después se entrega `OrdenCreada` al manejador. En sistemas distribuidos
se reemplazaría este ejemplo con el patrón outbox para publicar eventos de forma
fiable tras el commit.

## Ejecutar

```bash
poetry run pytest tests/lab_limpia_coches
```

Una migración gradual puede empezar envolviendo el acceso actual a datos en un
repositorio, extraer un caso de uso y, finalmente, sustituir llamadas directas
desde controladores por puertos inyectados.
