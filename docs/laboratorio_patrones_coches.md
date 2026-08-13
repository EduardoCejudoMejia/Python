# Laboratorio: patrones de diseño con coches

Este ejemplo aislado está en `src/app/lab_patrones_coches` y aplica tres
patrones al cálculo de precios de coches:

- **Strategy**: `PrecioNormal` y `PrecioOferta` son políticas sustituibles.
- **Decorator**: `ProveedorConCache` añade caché sin modificar el proveedor.
- **Adapter**: `AdaptadorProveedorExterno` traduce `consultar(codigo)` de una
  API ajena al puerto local `obtener_precio(coche)`.

`crear_estrategia` representa una Factory sencilla y `ServicioPrecios` ofrece
una fachada mínima para el caso de uso. `Coche` usa `dataclass` con `slots`:
un patrón idiomático para valores pequeños e inmutables.

## Ejecutar

```bash
poetry run pytest tests/lab_patrones_coches
```

Evita usar Singleton para el proveedor o la caché: introduce estado global,
dificulta aislar pruebas y puede causar datos obsoletos. Si aparecen muchos
`if tipo == ...` en el servicio, es una señal para introducir Strategy o una
Factory; si una API externa filtra su formato por todo el dominio, crea un
Adapter en su frontera.
