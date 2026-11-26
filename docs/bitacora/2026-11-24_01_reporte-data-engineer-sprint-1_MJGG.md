# Bitácora 01 · Reporte de ejecución · Data Engineer · Sprint 1

**Proyecto:** MLOps Green Data  
**Fecha:** 2026-11-24  
**Rol:** Data Engineer (DE)  
**Iniciales:** MJGG  
**Sprint:** 1 (24–28 nov) · Base del repo, datos y API base  
**Rama:** `de/sprint1-base` · **PR:** [#2](https://github.com/IscoAmariles/MLOps/pull/2)  
**Plan ejecutado:** [docs/plan-data-engineer.md](../plan-data-engineer.md)

## 1. Objetivo

Dejar lista la base técnica que el resto del equipo necesita para empezar: repositorio con ramas, copia versionada de los datos, dependencias, configuración central, carga y validación de datos, Prometheus y la API base con el contrato D2. La ruta crítica del sprint es **5 → 7.1 → 8.1**, porque el ML Engineer necesita `config.py` y `load_data()` para el paso 9.

## 2. Resultado por paso

| Paso | Tarea | Evidencia | Estado |
|---|---|---|---|
| 3 | Rama `dev` creada desde `main` | Rama `dev` en GitHub | Hecho |
| 3 | Proteger `main` (exigir PR) | GitHub no muestra protección en `main` | **Pendiente** (requiere admin del repo) |
| 4 | `.gitignore`, archivos base y `.gitkeep` | `.gitignore`, `src/features.py`, `tests/test_api.py`, `.gitkeep` en `app/`, `data/monitoring/`, `.github/workflows/`, `pytest.ini` | Hecho |
| 5 | Copia del Gold del ETL | `data/raw/gold_final.csv`: 20 filas × 12 columnas, idéntico al del commit `684fba9` del ETL | Hecho |
| 5 | `requirements.txt` | Python 3.12; `pandas==2.3.2` y `numpy==2.3.2` alineados con el ETL; incluye `streamlit`, `requests` y `httpx` | Hecho |
| 7.1 | `src/config.py` | `pathlib` + `PROJECT_DIR`; rutas de datos y log, `MODEL_NAME`, `MODEL_ALIAS`, `MODEL_URI`, URI de MLflow, `RANDOM_STATE`, columnas esperadas | Hecho |
| 7.2 | `docker/prometheus.yml` | Job `green-data-api`, target `host.docker.internal:8000`, scrape cada 5 s | Hecho |
| 8.1 | `src/data.py` con `load_data()` | Valida archivo, 12 columnas, no vacío, sin nulos en columnas clave y `Country_Code` único. Con el snapshot real devuelve 20 × 12 | Hecho |
| 8.2 | `docker-compose.yml` con Prometheus | Servicio en el puerto 9090; el archivo es válido (`docker compose config`) | Hecho · **falta levantarlo y abrir `localhost:9090`** |
| 11.2 | `api/main.py` base | `/health` y esquema D2 en `/predict`. Consumo 0, renovable > consumo e ingreso inexistente devuelven 422. Una entrada válida devuelve 503 hasta conectar el modelo | Hecho |
| 11.3 | README borrador | Requisitos, instalación, origen de los datos, tabla D1–D6 y estructura | Hecho |

## 3. Commits (a nombre de MajoGGezz)

| Commit | Mensaje |
|---|---|
| `5b3ad7f` | chore: .gitignore, archivos base y .gitkeep (paso 4) |
| `581282d` | feat(data): copia de gold_final.csv del ETL y requirements.txt (paso 5) |
| `83c754f` | feat: config.py, data.py con load_data(), prometheus.yml y docker-compose (pasos 7.1, 7.2, 8.1, 8.2) |
| `6ee0658` | feat(api): API base con /health y esquema D2; borrador del README (pasos 11.2, 11.3) |

## 4. Origen de los datos (decisión D5)

| Campo | Valor |
|---|---|
| Repo ETL | [AndreLopezRendon/Laboratorio-Apache-Airflow-](https://github.com/AndreLopezRendon/Laboratorio-Apache-Airflow-) (llamado `Laboratorio-MLOps-green-data-etl` en los planes) |
| Commit | `684fba9` |
| Archivo | `data/gold/gold_final.csv` → `data/raw/gold_final.csv` |
| Contenido verificado | 20 países, 12 columnas, sin nulos. `Income_Level`: High 10, Upper middle 7, Lower middle 3 (no hay `Low income`) |

## 5. Decisiones técnicas

| Decisión | Motivo |
|---|---|
| `/predict` ya existe en la API base y responde 503 | Así `/docs` muestra el esquema D2, las entradas inválidas dan 422 y el PO puede empezar Streamlit contra el contrato |
| `extra_hosts: host.docker.internal:host-gateway` en Prometheus | En Docker Desktop no hace falta, pero en Linux sí; así el compose funciona en cualquier máquina (paso 25) |
| `pytest.ini` con `pythonpath = .` | Permite `import src...` y `import api...` desde los tests sin instalar el paquete |
| `Low income` aceptado en la API | Es un nivel válido del World Bank aunque no esté en los datos; se documenta en el README |

## 6. Entregas a otros roles

| Para | Qué | Estado |
|---|---|---|
| ML Engineer | `config.py` y `load_data()` para el paso 9 | Listo al hacer merge del PR #2 a `dev`. Avisar al MLE |
| ML Engineer | Agregar `SEGMENT_NAMES` en `config.py` después del paso 10 | Comentario dejado en `config.py` |
| Product Owner | Esquema D2 y `/health` para empezar Streamlit (paso 17.2) | Listo al hacer merge. Avisar al PO |

## 7. Pendientes y alertas para el Scrum Master

1. **El PR #2 apunta a `main`, no a `dev`.** Según los acuerdos del equipo, `main` solo recibe merges desde `dev` al cerrar el sprint. Hay que cambiar la base del PR a `dev`.
2. **`main` sin protección** (paso 3). Lo activa el dueño del repo o un admin en *Settings → Branches*.
3. **Prometheus sin verificar en vivo** (paso 8.2). Falta `docker compose up -d` y abrir `localhost:9090`; el target de la API saldrá DOWN hasta que la API corra.
4. **Ceremonias y coordinación:** Sprint Planning 1 (paso 2, D1–D6), entorno de cada integrante con Python 3.12 (paso 6) y Review y Retro 1 (paso 15).
5. **D6 (unidades de energía):** sigue pendiente del PO.
6. **Revisión cruzada:** el PR #2 debe revisarlo el ML Engineer (acuerdo DE ↔ MLE).

## 8. Siguiente sprint (preparado, aún no aplicado)

Para el Sprint 2 ya están preparados los cambios de los pasos 17.1 (API completa con `/predict`, `/metrics` y log de predicciones), 17.4 (tests de `data.py`), 20.2 (CI) y 21 (Grafana). Se aplicarán en una rama nueva desde `dev` una vez se haga merge del PR #2.
