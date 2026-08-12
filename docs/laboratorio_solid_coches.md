# Laboratorio: SOLID aplicado a coches

El ejemplo vive en `src/app/lab_solid_coches` y es independiente del código de
la aplicación existente. El servicio depende del puerto `RepositorioCoches`,
definido mediante `Protocol`, no de SQLite ni de un diccionario.

| Principio | Aplicación en el laboratorio |
| --- | --- |
| SRP | `Coche` representa datos; `ServicioCoches` orquesta el caso de uso; cada repositorio persiste. |
| OCP | Se puede añadir otro adaptador que cumpla el `Protocol` sin editar el servicio. |
| LSP | Las mismas pruebas se ejecutan contra memoria y SQLite, y exigen el mismo comportamiento. |
| ISP | El puerto sólo expone `guardar`, `buscar_por_matricula` y `listar`. |
| DIP | El servicio recibe la abstracción `RepositorioCoches`; `crear_repositorio` actúa como provider/factory. |

## Ejecutar

```bash
poetry run pytest tests/lab_solid_coches
```

Para producción, el punto de entrada escogería el provider (`"sqlite"`, por
ejemplo) y lo inyectaría en `ServicioCoches`. Las pruebas pueden elegir el de
memoria, lo que reduce acoplamiento y evita una dependencia de infraestructura.
