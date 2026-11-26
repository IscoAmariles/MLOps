"""Predicción con el modelo champion (dueño: ML Engineer, paso 14).

La API llama a ``predict_segment()``; no repite lógica de modelo.
Prueba local (con el servidor de MLflow encendido)::

    python -m src.predict
"""

from functools import lru_cache

import mlflow
import mlflow.sklearn
import pandas as pd

from src import config
from src.features import RAW_INPUT_COLUMNS, encode_income


@lru_cache(maxsize=1)
def load_model():
    """Carga ``models:/green-data-segmentation@champion`` una sola vez."""
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    return mlflow.sklearn.load_model(config.MODEL_URI)


def predict_segment(energy_consumption: float, renewable_energy: float, income_level: str) -> dict:
    """Devuelve ``{"segment_id": int, "segment_name": str}`` (contrato D2)."""
    encode_income(income_level)  # ValueError si el nivel no existe
    X = pd.DataFrame(
        [[float(energy_consumption), float(renewable_energy), income_level]],
        columns=RAW_INPUT_COLUMNS,
    )
    segment_id = int(load_model().predict(X)[0])
    return {"segment_id": segment_id, "segment_name": config.SEGMENT_NAMES[segment_id]}


if __name__ == "__main__":
    for case in [
        ("EE. UU.", 1200, 20, "High income"),
        ("Colombia", 250, 35, "Upper middle income"),
        ("Noruega", 220, 200, "High income"),
    ]:
        print(case[0], "->", predict_segment(*case[1:]))
