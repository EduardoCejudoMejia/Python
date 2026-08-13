# Laboratorio: ciencia de datos con coches

El módulo `src/app/lab_ciencia_datos_coches` es independiente de la aplicación
existente y cubre un flujo mínimo de datos:

1. `cargar_y_limpiar` usa **Pandas** para leer el CSV, eliminar nulos y validar
   kilometrajes.
2. `entrenar_y_guardar` entrena un árbol de decisión de **scikit-learn** para
   clasificar coches como `seminuevo` o `usado`, y lo guarda con **joblib**.
3. `predecir_categoria` carga el artefacto y realiza una inferencia con año y
   kilometraje.

## Ejecutar

```bash
poetry install
poetry run pytest tests/lab_ciencia_datos_coches
```

El CSV de las pruebas se crea temporalmente: no se añaden datos ni modelos
binarios al repositorio. En un caso real, se separaría el conjunto de
entrenamiento del de evaluación y se registrarían métricas antes de publicar
un modelo.
