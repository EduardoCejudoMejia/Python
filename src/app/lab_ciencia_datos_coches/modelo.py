"""Carga CSV, entrenamiento y predicción mínima para el laboratorio."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

CARACTERISTICAS = ["anio", "kilometraje"]
COLUMNA_OBJETIVO = "categoria"


def cargar_y_limpiar(ruta_csv: str | Path) -> pd.DataFrame:
    """Lee coches, quita datos incompletos y normaliza los tipos numéricos."""
    datos = pd.read_csv(ruta_csv)
    columnas_requeridas = [*CARACTERISTICAS, COLUMNA_OBJETIVO]
    faltantes = set(columnas_requeridas) - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")

    limpios = datos.dropna(subset=columnas_requeridas).copy()
    limpios[CARACTERISTICAS] = limpios[CARACTERISTICAS].apply(
        pd.to_numeric, errors="coerce"
    )
    limpios = limpios.dropna(subset=CARACTERISTICAS)
    return limpios[limpios["kilometraje"] >= 0].reset_index(drop=True)


def entrenar_y_guardar(ruta_csv: str | Path, ruta_modelo: str | Path) -> Pipeline:
    """Entrena un clasificador básico y lo persiste con joblib."""
    datos = cargar_y_limpiar(ruta_csv)
    if datos.empty:
        raise ValueError("No hay filas válidas para entrenar.")

    modelo = Pipeline(
        [
            ("escalador", StandardScaler()),
            ("clasificador", DecisionTreeClassifier(max_depth=2, random_state=42)),
        ]
    )
    modelo.fit(datos[CARACTERISTICAS], datos[COLUMNA_OBJETIVO])
    joblib.dump(modelo, ruta_modelo)
    return modelo


def predecir_categoria(ruta_modelo: str | Path, anio: int, kilometraje: int) -> str:
    """Carga el modelo guardado y devuelve una categoría para un coche."""
    if kilometraje < 0:
        raise ValueError("El kilometraje no puede ser negativo.")

    modelo: Pipeline = joblib.load(ruta_modelo)
    entrada = pd.DataFrame([{"anio": anio, "kilometraje": kilometraje}])
    return str(modelo.predict(entrada)[0])
