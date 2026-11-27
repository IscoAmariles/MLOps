# Plan del Data Engineer (DE)

Tu parte del [plan del equipo](plan-equipo.md). Los números de paso son los del PDF *Paso a paso del Taller MLOps por rol*, y "(Guía: Paso X)" remite a la Guía del taller.

## Lo que necesitas saber

- **Eres dueño de:** el repo y el CI, la copia de los datos, `config.py`, `data.py`, la API, Docker Compose, Prometheus y Grafana. También asumes las tareas que en el PDF eran del Scrum Master (repo, CI, README base).
- **Datos:** el repo ETL deja `data/gold/gold_final.csv` (20 países, 12 columnas, sin nulos). Es la fuente; no usamos Airflow, el Postgres del ETL ni la API del World Bank.
- **Contrato propuesto de `/predict` (D2):**
  - Entrada: `energy_consumption` (> 0), `renewable_energy` (≥ 0 y ≤ `energy_consumption`), `income_level` (`Low income`, `Lower middle income`, `Upper middle income` o `High income`).
  - Salida: `segment_id` y `segment_name`.
  - Entrada inválida: error 422.
- **Nombres (D3 y D4):** modelo `green-data-segmentation`, alias `champion`, métricas `green_data_prediction_count_total` y `green_data_segment_predictions_total`.
- **Ceremonias:** las facilita el Scrum Master (Francisco), que también organiza el ensayo de la demo (paso 26) y revisa y hace merge de los PR. Tú participas en todas.

## Resumen

| Sprint | Pasos tuyos | Qué entregas | Qué esperas de otros |
|---|---|---|---|
| 1 | 2, 3, 4, 5, 6, 7.1, 7.2, 8.1, 8.2, 11.2, 11.3, 15 | Repo, datos, `config.py`, `data.py`, Prometheus, API base | PO: reglas de D2 y D6 |
| 2 | 17.1, 17.4 (datos), 18, 20.1, 20.2, 21 | API completa, tests de datos, CI, Grafana | MLE: `predict_segment()` y `champion` (paso 14) |
| 3 | 23, 24.2, 24.4, 25, 26 | CI en verde, tag, dashboard exportado | PO: README y guion (paso 24.1) |

---

## Sprint 1 (24–28 nov)

Ruta crítica del sprint: **5 → 7.1 → 8.1**. El MLE necesita `config.py` y `load_data()` para empezar el paso 9.

### Paso 2 — Sprint Planning 1 (facilita SM)
- [ ] Registrar en el README el resultado de D1–D6 cuando el equipo las cierre.
- [ ] Confirmar que el contrato D2 y los nombres D3/D4 quedan aceptados antes de salir.

### Paso 3 — Repo en GitHub (Guía: Paso 19, adelantado)
- [ ] Crear el repo remoto y conectarlo: `git remote add origin <url>`.
- [ ] Primer commit en `main` con lo que ya existe (`docs/`).
- [ ] Crear `dev` desde `main`.
- [ ] Invitar a los otros tres integrantes. Por decisión del equipo, `main` no se protege (ver la sección 3 del plan del equipo).

**Hecho cuando:** los cuatro integrantes tienen acceso de escritura al repo.

### Paso 4 — Archivos base (Guía: Pasos 0–2)
Las carpetas ya existen (la estructura está en la sección 5 del plan del equipo).
- [ ] Crear el entorno virtual y `.gitignore` con: `.venv/`, `__pycache__/`, `.env`, `mlruns/`, `mlartifacts/` y `data/monitoring/*.csv`.
- [ ] Crear `src/features.py` y `tests/test_api.py` como archivos base.
- [ ] **Git no versiona carpetas vacías.** Agrega un `.gitkeep` en las que aún no tengan archivos (`data/monitoring/`, `app/`, `.github/workflows/`).
- [ ] Subir a `dev` por PR.

### Paso 5 — Datos y dependencias (Guía: Pasos 3–4)
- [ ] Copiar el Gold del ETL como `data/raw/gold_final.csv`:
  ```powershell
  Copy-Item <ruta-al-repo-ETL>\data\gold\gold_final.csv data\raw\gold_final.csv
  ```
- [ ] Anotar en el README el origen: repo `Laboratorio-MLOps-green-data-etl`, commit `684fba9`, archivo `data/gold/gold_final.csv`.
- [ ] Llenar `requirements.txt` según la Guía (Paso 4) alineando `pandas==2.3.2` y `numpy==2.3.2` con el ETL. Confirma con MLE y PO que están sus librerías (por ejemplo `streamlit`, `requests` y, para los tests de la API, `httpx`).
- [ ] Subir por PR.

**Hecho cuando:** `data/raw/gold_final.csv` está en el repo y el origen está documentado.

### Paso 6 — Entorno de cada integrante
- [ ] Acordar una misma versión de Python (el ETL declara 3.12).
- [ ] Cada uno clona, crea su `.venv` e instala `requirements.txt`. Ayuda a quien se atasque.

### Paso 7.1 — `src/config.py` (Guía: Paso 5)
- [ ] Reutilizar el patrón del `config.py` del ETL: `pathlib`, variable de entorno `PROJECT_DIR` y nunca rutas de Windows escritas a mano.
- [ ] Definir al menos: ruta de `data/raw/gold_final.csv`, ruta del log `data/monitoring/api_predictions_log.csv`, `MODEL_NAME = "green-data-segmentation"`, `MODEL_ALIAS = "champion"`, URI de MLflow `http://127.0.0.1:5000` y `RANDOM_STATE`.
- [ ] Después del paso 10, el MLE agrega aquí `SEGMENT_NAMES` (id → nombre) por PR.

**Hecho cuando:** ningún otro módulo escribe rutas a mano.

### Paso 7.2 — `docker/prometheus.yml` (Guía: Paso 15)
- [ ] Un *job* para la API: `metrics_path: /metrics` y *target* `host.docker.internal:8000`. La API corre en el host y Prometheus en Docker, así que `localhost` no sirve.
- [ ] Intervalo de scrape corto (por ejemplo 5 s) para que la demo muestre los cambios rápido.

### Paso 8.1 — `src/data.py` (Guía: Paso 6)
- [ ] `load_data()` carga `data/raw/gold_final.csv` y valida con el estilo de `validate_bronze` del ETL (`FileNotFoundError` / `ValueError` con mensaje claro):
  - el archivo existe;
  - tiene las 12 columnas esperadas;
  - no está vacío (el snapshot tiene 20 filas);
  - no hay nulos en `Country_Code`, `Energy_Consumption` ni `Renewable_Energy`;
  - `Country_Code` es único.
- [ ] Avisar al MLE en cuanto se haga merge: es la entrada del paso 9.

**Hecho cuando:** `load_data()` devuelve el DataFrame y falla con un mensaje claro si el archivo está mal.

### Paso 8.2 — `docker-compose.yml` (Guía: Pasos 16–17)
- [ ] Servicio de Prometheus (puerto 9090) con `docker/prometheus.yml` montado. Grafana se agrega en el paso 21.
- [ ] Ejecutar `docker compose up -d` y abrir `http://localhost:9090`.
- [ ] El *target* de la API aparecerá DOWN hasta que la API corra: es lo esperado.
- [ ] Si tienes el stack de Airflow del ETL encendido, apágalo (`docker compose down` dentro de `airflow/`). Pide al menos 4 GB de RAM.

**Hecho cuando:** Prometheus abre en `localhost:9090`.

### Paso 11.2 — `api/main.py` base (Guía: Paso 12, parcial)
- [ ] App FastAPI con `/health`.
- [ ] Modelo Pydantic con el esquema D2 y sus reglas: `energy_consumption > 0`, `0 ≤ renewable_energy ≤ energy_consumption`, `income_level` en la lista de 4 valores.
- [ ] Ejecutar con `uvicorn api.main:app --port 8000` (o el comando de la Guía) y probar en `http://localhost:8000/docs`.
- [ ] Avisar al PO: con esto puede empezar Streamlit.

**Hecho cuando:** `/docs` muestra el esquema y 3 entradas inválidas devuelven 422 (consumo 0, renovable > consumo, nivel de ingreso inexistente).

### Paso 11.3 — README base (Guía: Paso 19)
- [ ] Borrador con requisitos, instalación (venv, `pip install`) y el origen de los datos. El PO lo completa en el paso 24.1.
- La revisión y el merge de los PR los hace el SM.

### Paso 15 — Review y Retro 1 (facilita SM)
- [ ] Mostrar al PO la API en `localhost:8000/docs` (esquema y 422) y Prometheus en `localhost:9090`.

---

## Sprint 2 (1–5 dic)

Ruta crítica: **14 (MLE) → 17.1 → 18 → 20.1 → 21**.

### Paso 17.1 — API completa (Guía: Paso 12)
- [ ] `POST /predict`: valida con el esquema, llama a `predict_segment()` del MLE (no repitas lógica de modelo en la API) y devuelve `segment_id` y `segment_name`.
- [ ] `GET /metrics` con `prometheus_client`:
  - contador `green_data_prediction_count` (el cliente expone `_total`);
  - contador `green_data_segment_predictions` con etiqueta `segment` (el nombre del segmento).
- [ ] Log de predicciones en `data/monitoring/api_predictions_log.csv`: crear el archivo con encabezado si no existe y agregar **una fila por predicción válida** (fecha-hora, los 3 inputs, `segment_id`, `segment_name`). Las entradas inválidas no cuentan ni se registran.
- [ ] Si el modelo no carga (MLflow caído), `/predict` responde 503 con un mensaje claro, sin tumbar la API.

**Hecho cuando:** una predicción válida suma al contador y agrega una fila al log.

### Paso 17.4 — Tests de datos (Guía: Pasos 6–7)
- [ ] Tests de `src/data.py` con `tmp_path`: archivo faltante, columna faltante, archivo vacío, `Country_Code` duplicado, y el snapshot real carga 20 filas.
- [ ] Los tests de `features.py` los escribe el MLE.

### Paso 18 — Integrar API y `champion`, con el MLE (Guía: Pasos 11–12)
- [ ] Con el servidor de MLflow encendido, probar `/predict` en `http://localhost:8000/docs` con casos reales.
- [ ] Revisar que la API no recargue el modelo en cada petición.

**Hecho cuando:** `/predict` responde correctamente con el modelo real.

### Paso 20.1 — Consultas en Prometheus (Guía: Paso 17)
- [ ] En `http://localhost:9090` → *Status → Targets*, el *target* de la API en UP.
- [ ] Consultar `green_data_prediction_count_total` y `green_data_segment_predictions_total` después de hacer predicciones.

### Paso 20.2 — CI (Guía: Paso 20)
- [ ] `.github/workflows/ci.yml` en push y en PR: *checkout*, instalar Python (versión acordada), `pip install -r requirements.txt` y `pytest`.
- [ ] El CI no puede depender de MLflow ni de Docker: los tests de la API usan un modelo simulado (paso 17.3 del MLE).

**Hecho cuando:** el workflow corre en cada push y termina en verde.

### Paso 21 — Grafana (Guía: Paso 18)
- [ ] Agregar Grafana a `docker-compose.yml` (puerto 3000).
- [ ] Fuente de datos Prometheus con URL `http://prometheus:9090` (nombre del servicio dentro de la red del compose).
- [ ] Dashboard con las consultas del taller:
  - total de predicciones: `green_data_prediction_count_total`;
  - predicciones por segmento: `sum by (segment) (green_data_segment_predictions_total)`.

**Hecho cuando:** una predicción hecha desde Streamlit aparece en el dashboard.

### Paso 22 — Review y Retro 2
- [ ] Hacer la demo técnica de Grafana para el PO.

---

## Sprint 3 (8–11 dic)

### Paso 23 — Sprint Planning 3 (facilita SM)

### Paso 24.2 — CI en verde y tag (Guía: Pasos 19–20)
- [ ] Comprobar que el CI está en verde en el último commit de `main`.
- [ ] Crear el tag de versión sobre ese commit (propuesta: `v1.0.0`) y subirlo: `git tag v1.0.0` y `git push origin v1.0.0`.

### Paso 24.4 — Exportar el dashboard (Guía: Paso 18)
- [ ] En Grafana: *Share → Export → Export as JSON* (marcando "exportar para compartir externamente" para que la fuente de datos sea una variable).
- [ ] Guardarlo en `docker/` (por ejemplo `docker/grafana_dashboard.json`) y subirlo por PR.

**Hecho cuando:** el JSON se importa bien en un Grafana nuevo (`docker compose down -v` y levantar de nuevo).

### Paso 25 — Prueba cruzada
- [ ] Correr todo en una máquina que no sea la tuya siguiendo solo el README. Corregir lo que falle.

### Paso 26 — Ensayo de la demo (organiza SM; el PO presenta)
- [ ] Tener la API, Prometheus y Grafana corriendo antes de empezar, y revisar con el SM el orden de arranque.
