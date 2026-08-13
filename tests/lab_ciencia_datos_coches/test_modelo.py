from pathlib import Path

import pandas as pd
import pytest

from app.lab_ciencia_datos_coches import (
    cargar_y_limpiar,
    entrenar_y_guardar,
    predecir_categoria,
)


@pytest.fixture
def ruta_csv(tmp_path: Path) -> Path:
    ruta = tmp_path / "coches.csv"
    ruta.write_text(
        "anio,kilometraje,categoria\n"
        "2024,5000,seminuevo\n"
        "2023,18000,seminuevo\n"
        "2015,120000,usado\n"
        "2012,180000,usado\n"
        "2020,,seminuevo\n"
        "2018,-1,usado\n"
    )
    return ruta


def test_cargar_y_limpiar_descarta_filas_incompletas_o_invalidas(
    ruta_csv: Path,
) -> None:
    datos = cargar_y_limpiar(ruta_csv)

    assert len(datos) == 4
    assert list(datos.columns) == ["anio", "kilometraje", "categoria"]
    assert pd.api.types.is_numeric_dtype(datos["kilometraje"])


def test_entrenamiento_serializa_el_modelo_y_permite_inferencia(
    ruta_csv: Path, tmp_path: Path
) -> None:
    ruta_modelo = tmp_path / "clasificador.joblib"

    entrenar_y_guardar(ruta_csv, ruta_modelo)

    assert ruta_modelo.exists()
    assert predecir_categoria(ruta_modelo, anio=2024, kilometraje=3_000) == "seminuevo"
    assert predecir_categoria(ruta_modelo, anio=2012, kilometraje=190_000) == "usado"


def test_limpieza_valida_columnas_requeridas(tmp_path: Path) -> None:
    ruta_csv = tmp_path / "incompleto.csv"
    ruta_csv.write_text("anio,categoria\n2024,seminuevo\n")

    with pytest.raises(ValueError, match="Faltan columnas"):
        cargar_y_limpiar(ruta_csv)


def test_inferencia_rechaza_kilometraje_negativo(
    ruta_csv: Path, tmp_path: Path
) -> None:
    ruta_modelo = tmp_path / "clasificador.joblib"
    entrenar_y_guardar(ruta_csv, ruta_modelo)

    with pytest.raises(ValueError, match="no puede ser negativo"):
        predecir_categoria(ruta_modelo, anio=2024, kilometraje=-1)
