# MLOps Green Data

Segmentación de países según su consumo de energía, su energía renovable y su
nivel de ingreso, con el flujo MLOps del taller: datos versionados, modelo
registrado en MLflow, API con FastAPI, interfaz en Streamlit y monitoreo con
Prometheus y Grafana.

> **Aviso:** los datos de energía son **datos de laboratorio, no estadísticas
> oficiales** (así lo indica el repo ETL de origen).

## Requisitos

- Python 3.12
- Git
- Docker Desktop (para Prometheus y Grafana), con al menos 4 GB de RAM

## Instalación

```powershell
git clone https://github.com/IscoAmariles/MLOps.git
cd MLOps
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

## Datos

| Campo | Valor |
|---|---|
| Archivo en este repo | `data/raw/gold_final.csv` (20 países, 12 columnas, sin nulos) |
| Repo de origen | Repo ETL del equipo ([AndreLopezRendon/Laboratorio-Apache-Airflow-](https://github.com/AndreLopezRendon/Laboratorio-Apache-Airflow-)), llamado `Laboratorio-MLOps-green-data-etl` en los planes |
| Commit de origen | `684fba9` |
| Archivo de origen | `data/gold/gold_final.csv` (capa Gold) |

El proyecto usa esta copia y no necesita Airflow, el Postgres del ETL ni la API
del World Bank (decisión D5). `src/data.py` (`load_data()`) la carga y valida.

## Cómo correr (borrador, lo completa el PO en el paso 24.1)

```powershell
# Tests
pytest

# API  ->  http://localhost:8000/docs
uvicorn api.main:app --port 8000

# Prometheus  ->  http://localhost:9090
docker compose up -d
```

Si tienes encendido el stack de Airflow del ETL, apágalo antes
(`docker compose down` dentro de `airflow/`).

## Decisiones del Sprint Planning 1

Se confirman en el paso 2 (detalle en [docs/plan-equipo.md](docs/plan-equipo.md)).

| # | Decisión | Resultado |
|---|---|---|
| D1 | Qué predice el modelo | Segmento de país creado con KMeans. `Environmental_Status` no es el target. |
| D2 | Contrato de `/predict` | Entrada: `energy_consumption` (> 0), `renewable_energy` (≥ 0 y ≤ consumo), `income_level` (4 niveles del World Bank). Salida: `segment_id`, `segment_name`. Inválido → 422. |
| D3 | Modelo y métrica | `green-data-segmentation`, alias `champion`, F1 macro. |
| D4 | Métricas Prometheus | `green_data_prediction_count_total`, `green_data_segment_predictions_total` |
| D5 | Origen de los datos | Copia de `gold_final.csv` (commit `684fba9`) en `data/raw/`. |
| D6 | Unidades de energía | Pendiente: el PO consulta al autor del ETL. |

`Low income` no aparece en los datos: la API lo acepta como el nivel ordinal más
bajo, pero el modelo nunca lo vio.

## Estructura

```
api/            API FastAPI
app/            Interfaz Streamlit
data/raw/       Copia del Gold del ETL
data/monitoring Log de predicciones (no se versiona)
docker/         Configuración de Prometheus y Grafana
docs/           Planes del equipo
src/            config, datos, features, entrenamiento y predicción
tests/          Tests (pytest)
```
