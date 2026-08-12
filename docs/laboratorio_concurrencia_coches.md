# Laboratorio: concurrencia y rendimiento con coches

El código está aislado en `src/app/lab_concurrencia_coches/` y no usa la API
existente. `CocheFetcher` consulta fichas JSON de coches de tres formas:

- `obtener_fichas_sincrono`: línea base, petición por petición.
- `obtener_fichas_con_hilos`: E/S bloqueante mediante `ThreadPoolExecutor`.
- `obtener_fichas_async`: E/S concurrente con `httpx.AsyncClient`, `async/await`
  y un semáforo que protege al servicio remoto.

Para trabajo CPU-bound se incluye `calcular_desgastes_en_procesos`, que utiliza
`ProcessPoolExecutor`. Los procesos tienen intérpretes separados y por ello no
compiten por el GIL como lo harían los hilos. El coste de crear y comunicar con
procesos hace que sólo convenga para cálculos suficientemente grandes.

## Ejecutar las pruebas

```bash
poetry run pytest tests/lab_concurrencia_coches
```

Las pruebas usan `httpx.MockTransport`: son reproducibles, no necesitan red y
comprueban que nunca haya más de dos peticiones asíncronas simultáneas.

## Medición

`medir_sincrono(urls)` usa `timeit` y debe apuntar a un servidor local de
pruebas o a un endpoint controlado. Para ver dónde emplea tiempo un cálculo:

```python
from app.lab_concurrencia_coches.fetcher import perfilar_calculo

perfil = perfilar_calculo(1_000_000)
perfil.print_stats(sort="cumulative")
```

Al comparar modelos, mantén el mismo conjunto de URLs, repite varias veces y
separa E/S (asyncio/hilos) de CPU (procesos). No midas contra Internet abierto:
la latencia variable ocultaría el efecto de la concurrencia.
