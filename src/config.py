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

# --- Segmentación y entrenamiento (MLE, pasos 9-12) --------------------------
REPORTS_DIR = PROJECT_DIR / "reports"

# Elegidos con `python -m src.clustering` (ver reports/clustering_k_selection.csv).
CLUSTER_K = 3
# log1p del consumo + Renewable_Share, sin ingreso: mejor silhouette con k=3 (0,41).
# income_level se sigue aceptando en /predict (contrato D2), pero no segmenta.
CLUSTER_VARIANT = "log_sin_ingreso"
# Mínimo de países por segmento. Con 20 países ningún k=3 llega a 4 (los líderes
# renovables son 3), así que se fijó en 3: es lo que exige CV estratificada de 3 folds.
MIN_SEGMENT_SIZE = 3
CV_FOLDS = 3

# Nombres de negocio por segmento (paso 10). PROPUESTA del MLE: los aprueba el PO.
# Los ids se ordenan por Renewable_Share medio: 0 = el menos renovable.
SEGMENT_NAMES = {
    0: "Grandes consumidores poco renovables",
    1: "Transición intermedia",
    2: "Líderes renovables",
}
SEGMENT_DESCRIPTIONS = {
    0: "Consumo alto (≈1000 en promedio) y menos del 10 % renovable; "
    "p. ej. China, EE. UU., India, Alemania.",
    1: "Consumo moderado (≈280) con una participación renovable media (≈17 %); "
    "p. ej. Colombia, México, España, Australia.",
    2: "Consumo bajo (≈95) cubierto en su mayoría por renovables (≈79 %); "
    "Noruega, Uruguay y Kenia.",
}
