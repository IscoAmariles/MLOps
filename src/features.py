"""Ingeniería de variables (dueño: ML Engineer, paso 9).

Entrenamiento y API reciben exactamente las mismas columnas crudas, las del
contrato D2 (``RAW_INPUT_COLUMNS``). Toda transformación vive en el ``Pipeline``
que devuelve ``make_preprocessor``, así la API no reimplementa nada.

No se usa ``Energy_per_Renewable_Unit``: el ETL la calcula con ``+1`` en el
denominador y habría que replicarla idéntica en la API.
"""

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src import config

# Columnas del contrato D2 (entrada de /predict).
RAW_INPUT_COLUMNS = ["energy_consumption", "renewable_energy", "income_level"]

# Columnas que salen de build_features (con ingreso).
FEATURE_COLUMNS = ["energy_consumption", "renewable_share", "income_ordinal"]

# Low income 0 ... High income 3. Un solo origen: config.INCOME_LEVELS.
INCOME_ORDINAL = {level: i for i, level in enumerate(config.INCOME_LEVELS)}

_GOLD_TO_RAW = {
    "Energy_Consumption": "energy_consumption",
    "Renewable_Energy": "renewable_energy",
    "Income_Level": "income_level",
}


def renewable_share(consumption, renewable):
    """``renewable / consumption``. Consumo ≤ 0 → NaN (mismo criterio que el ETL).

    Acepta escalares o Series.
    """
    if np.isscalar(consumption):
        return renewable / consumption if consumption > 0 else float("nan")
    consumption = pd.Series(consumption, dtype=float)
    return pd.Series(renewable, dtype=float) / consumption.where(consumption > 0)


def encode_income(level: str) -> int:
    """Mapeo ordinal del nivel de ingreso del World Bank."""
    try:
        return INCOME_ORDINAL[level]
    except KeyError:
        raise ValueError(
            f"income_level desconocido: {level!r}. Valores válidos: {config.INCOME_LEVELS}."
        ) from None


def gold_to_raw_inputs(df: pd.DataFrame) -> pd.DataFrame:
    """Pasa las columnas del Gold a las del contrato D2."""
    return df[list(_GOLD_TO_RAW)].rename(columns=_GOLD_TO_RAW).reset_index(drop=True)


def build_features(
    X: pd.DataFrame, log_consumption: bool = True, use_income: bool = True
) -> pd.DataFrame:
    """De las columnas crudas a las variables del modelo."""
    X = pd.DataFrame(X, columns=RAW_INPUT_COLUMNS).reset_index(drop=True)
    consumption = X["energy_consumption"].astype(float)
    out = pd.DataFrame(
        {
            "energy_consumption": np.log1p(consumption) if log_consumption else consumption,
            "renewable_share": renewable_share(consumption, X["renewable_energy"]),
        }
    )
    if use_income:
        out["income_ordinal"] = X["income_level"].map(encode_income)
    return out


def make_preprocessor(log_consumption: bool = True, use_income: bool = True) -> Pipeline:
    """``Pipeline`` de preprocesamiento: variables derivadas + estandarización."""
    return Pipeline(
        [
            (
                "features",
                FunctionTransformer(
                    build_features,
                    kw_args={"log_consumption": log_consumption, "use_income": use_income},
                ),
            ),
            ("scaler", StandardScaler()),
        ]
    )
