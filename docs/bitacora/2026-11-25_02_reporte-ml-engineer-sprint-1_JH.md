# Bitácora 02 · Reporte de ejecución · ML Engineer · Sprint 1

**Proyecto:** MLOps Green Data  
**Fecha:** 2026-11-25  
**Rol:** ML Engineer (MLE)  
**Iniciales:** JH  
**Sprint:** 1 (24–28 nov) · Segmentos, modelo y `champion`  
**Rama:** `mle/sprint1-modelo`  
**Plan ejecutado:** [docs/plan-ml-engineer.md](../plan-ml-engineer.md)

## 1. Objetivo

Crear los segmentos de países con KMeans, entrenar y comparar los 3 modelos del taller en MLflow, registrar el mejor como `green-data-segmentation@champion` y dejar `predict_segment()` listo para que el DE lo conecte a la API (paso 17.1). Ruta crítica: **9 → 10 → 12 → 13 → 14**.

Se trabajó con TDD: primero los tests de cada módulo (rojo) y después el código (verde).

## 2. Resultado por paso

| Paso | Tarea | Evidencia | Estado |
|---|---|---|---|
| 9 | `src/features.py` | `renewable_share` (consumo 0 → NaN, igual que el ETL), mapeo ordinal de ingreso desde `config.INCOME_LEVELS`, `Pipeline` con `log1p` opcional y `StandardScaler` | Hecho |
| 9 | `src/clustering.py` | `evaluate_k` (4 variantes × k = 2…5), `fit_segments` con ids estables (ordenados por share renovable), `segment_report`. Tabla en `reports/clustering_k_selection.csv` | Hecho |
| 10 | Nombres de segmentos | Propuesta del MLE en `config.SEGMENT_NAMES` y `SEGMENT_DESCRIPTIONS` | **Pendiente de aprobación del PO** |
| 11.1 | Servidor de MLflow | `mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts` | Hecho |
| 12 | `src/train.py` | 3 runs en el experimento `green-data-segmentation` con parámetros, F1 macro medio y desviación | Hecho |
| 13 | `champion` | `models:/green-data-segmentation@champion` → versión 1 (Logistic Regression), carga y predice | Hecho |
| 14 | `src/predict.py` | `predict_segment()` correcto para un caso por segmento (EE. UU. → 0, Colombia → 1, Noruega → 2) | Hecho |
| — | Tests | `test_features`, `test_clustering`, `test_train`, `test_predict`: **35 pasan**. Sin MLflow corren con modelo simulado (el de integración se omite) | Hecho |

## 3. Segmentos (k = 3, variante `log_sin_ingreso`)

Variables: `log1p(energy_consumption)` y `renewable_share`, estandarizadas. Silhouette 0,41.

| id | Nombre propuesto | n | Consumo medio | Share renovable medio | Países |
|---|---|---|---|---|---|
| 0 | Grandes consumidores poco renovables | 8 | 1075 | 0,09 | Brasil, Canadá, China, Francia, Alemania, India, Japón, EE. UU. |
| 1 | Transición intermedia | 9 | 277 | 0,17 | Argentina, Australia, Chile, Colombia, Egipto, México, Perú, Sudáfrica, España |
| 2 | Líderes renovables | 3 | 95 | 0,79 | Kenia, Noruega, Uruguay |

Cruce con `Environmental_Status` (solo para validar, no es entrada ni target):

| Segmento | Critical | Green | Moderate |
|---|---|---|---|
| 0 | 5 | 0 | 3 |
| 1 | 4 | 3 | 2 |
| 2 | 0 | 3 | 0 |

## 4. Comparación de modelos (CV estratificada, 3 folds, F1 macro)

| Modelo | F1 medio | Desviación | Folds |
|---|---|---|---|
| **Logistic Regression** (champion) | **0,962** | 0,054 | 1,00 · 0,89 · 1,00 |
| Random Forest | 0,924 | 0,054 | 0,89 · 0,89 · 1,00 |
| Gradient Boosting | 0,801 | 0,206 | 0,89 · 0,52 · 1,00 |

Regla de desempate, fijada antes de entrenar: mayor F1 medio, luego menor desviación, luego el modelo más simple. Ganó Logistic Regression por F1 medio.

## 5. Decisiones técnicas

| Decisión | Motivo |
|---|---|
| **Mínimo de 3 países por segmento** (el plan decía "unos 4") | Con 20 países ninguna opción con k = 3 llega a 4: los líderes renovables siempre son 3. La única con mínimo 4 era k = 2 (16 vs 4), poco informativa. CV estratificada de 3 folds funciona con 3. Decidido con Jean el 25 nov |
| **`income_level` no entra al clustering** | Sin ingreso el silhouette con k = 3 es mejor (0,41 contra 0,40) y los grupos coinciden con la hipótesis del PO. La API lo sigue aceptando y validando (contrato D2), pero el `champion` no lo usa |
| El `Pipeline` registrado recibe las columnas crudas del contrato D2 | La API pasa los 3 campos tal cual y no reimplementa el escalado |
| `skops_trusted_types=["src.features.build_features"]` y `code_paths=["src"]` | MLflow 3.18 serializa con skops y exige declarar las funciones propias. `code_paths` permite cargar el modelo en otra máquina |
| Backend `sqlite:///mlflow.db` | MLflow 3 recomienda una base de datos en lugar de `mlruns/`. Ambos están en `.gitignore` |
| Python 3.12.10 | Versión acordada por el equipo (la del ETL) |

## 6. Entregas a otros roles

| Para | Qué | Estado |
|---|---|---|
| Data Engineer | `from src.predict import predict_segment` para `/predict` (paso 17.1). Lanza `ValueError` con un ingreso desconocido; si MLflow está caído, la carga del modelo lanza una excepción → la API debe responder 503 | Listo al hacer merge |
| Product Owner | Tabla de segmentos (sección 3) para aprobar o cambiar los nombres (paso 10). Las descripciones de `config.SEGMENT_DESCRIPTIONS` sirven para Streamlit | Pendiente de su revisión |

## 7. Pendientes y alertas

1. **PO:** aprobar o cambiar los nombres de los segmentos (paso 10). Si los cambia, se edita solo `config.SEGMENT_NAMES`.
2. **`dev` estaba atrasada respecto a `main`** (el PR #2 se fusionó en `main`). Se abrió el [PR #3](https://github.com/IscoAmariles/MLOps/pull/3) `main → dev`. Esta rama parte de `main`, así que su PR a `dev` muestra también los commits del DE hasta que se fusione el #3.
3. **Revisión cruzada:** el DE revisa este PR (acuerdo DE ↔ MLE).
4. **Límites del modelo** (se desarrollan en el paso 24.3): solo 20 países con datos de laboratorio, y los segmentos salen de las mismas variables que el modelo predice, así que un F1 alto es esperable y no demuestra capacidad de generalizar.
