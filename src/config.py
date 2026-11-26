"""Rutas y parámetros del proyecto (paso 7.1).

Mismo patrón que el ``config.py`` del repo ETL: todo se arma con ``pathlib`` a
partir de ``PROJECT_DIR``. Ningún otro módulo debe escribir rutas a mano.

``PROJECT_DIR`` se puede fijar con una variable de entorno; si no existe, se usa
la raíz del repo (la carpeta que contiene ``src/``).
"""

import os
from pathlib import Path

# --- Rutas -------------------------------------------------------------------
PROJECT_DIR = Path(
    os.getenv("PROJECT_DIR", Path(__file__).resolve().parents[1])
).resolve()

DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
MONITORING_DIR = DATA_DIR / "monitoring"

# Copia del Gold del ETL (decisión D5).
RAW_DATA_PATH = RAW_DATA_DIR / "gold_final.csv"

# Log de predicciones que escribe la API (paso 17.1).
PREDICTIONS_LOG_PATH = MONITORING_DIR / "api_predictions_log.csv"

# --- Esquema del Gold --------------------------------------------------------
EXPECTED_COLUMNS = [
    "Country",
    "Country_Code",
    "Capital_City",
    "Region",
    "Income_Level",
    "Longitude",
    "Latitude",
    "Energy_Consumption",
    "Renewable_Energy",
    "Energy_per_Renewable_Unit",
    "Renewable_Share",
    "Environmental_Status",
]

# Columnas que no pueden tener nulos.
REQUIRED_NON_NULL_COLUMNS = ["Country_Code", "Energy_Consumption", "Renewable_Energy"]

# Niveles de ingreso del World Bank aceptados por /predict (decisión D2).
INCOME_LEVELS = [
    "Low income",
    "Lower middle income",
    "Upper middle income",
    "High income",
]

# --- Modelo y MLflow (decisión D3) -------------------------------------------
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
EXPERIMENT_NAME = "green-data-segmentation"
MODEL_NAME = "green-data-segmentation"
MODEL_ALIAS = "champion"
MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"

RANDOM_STATE = 42

# Después del paso 10 el MLE agrega aquí SEGMENT_NAMES (id -> nombre) por PR.
