# Laboratorio: pruebas y TDD con coches

La historia implementada es: **como propietario, quiero cargar combustible y conducir mi coche para conocer su kilometraje y combustible restante**. Al superar 10 000 km, el coche solicita una revisión.

El ejemplo contiene una sola clase de dominio: `Coche`, en `src/app/lab_tdd_cars/coche.py`.

## Ciclo TDD propuesto

1. Escribe una prueba que describa el comportamiento esperado: por ejemplo, `test_conducir_reduce_combustible_y_aumenta_kilometraje`.
2. Ejecútala y verifica que falle (rojo).
3. Implementa sólo lo necesario en `Coche` para que pase (verde).
4. Refactoriza manteniendo las pruebas en verde.

La suite muestra los elementos del módulo:

- `coche`: fixture reutilizable de pytest.
- `@pytest.mark.parametrize`: casos equivalentes para carga, validación y trayectos.
- `@pytest.mark.propiedades` y Hypothesis: verifica el balance de combustible con entradas generadas.
- `Mock`: comprueba la interacción con un notificador, sin servicio externo real.

## Ejecutar

```bash
poetry install --with dev
poetry run pytest --cov --cov-report=term-missing
```

El umbral está configurado en 100 % para `app.lab_tdd_cars`. GitHub Actions ejecuta el mismo comando en cada `push` y `pull request`.
