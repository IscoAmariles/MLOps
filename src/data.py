"""Carga y validación de los datos (paso 8.1).

Mismo estilo que ``validate_bronze`` del ETL: si algo está mal se lanza
``FileNotFoundError`` o ``ValueError`` con un mensaje claro.
"""

from pathlib import Path

import pandas as pd

from src import config


def validate_data(df: pd.DataFrame) -> None:
    """Valida el Gold cargado. Lanza ``ValueError`` si no cumple el esquema."""
    missing = [c for c in config.EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Faltan columnas en el dataset: {missing}. "
            f"Se esperan las {len(config.EXPECTED_COLUMNS)} columnas del Gold del ETL."
        )

    if df.empty:
        raise ValueError("El dataset está vacío (0 filas).")

    nulls = {
        col: int(df[col].isna().sum())
        for col in config.REQUIRED_NON_NULL_COLUMNS
        if df[col].isna().any()
    }
    if nulls:
        raise ValueError(f"Hay valores nulos en columnas obligatorias: {nulls}.")

    duplicated = df.loc[df["Country_Code"].duplicated(), "Country_Code"].tolist()
    if duplicated:
        raise ValueError(f"Country_Code debe ser único. Duplicados: {duplicated}.")


def load_data(path: Path | str | None = None) -> pd.DataFrame:
    """Carga ``data/raw/gold_final.csv`` (o ``path``) y lo valida.

    Devuelve el DataFrame tal como viene del Gold del ETL.
    """
    path = Path(path) if path is not None else config.RAW_DATA_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de datos: {path}. "
            "Copia data/gold/gold_final.csv del repo ETL a data/raw/gold_final.csv."
        )

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"El archivo {path} está vacío.") from exc

    validate_data(df)
    return df
