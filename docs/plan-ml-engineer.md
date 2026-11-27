# Plan del ML Engineer (MLE)

Tu parte del [plan del equipo](plan-equipo.md). Los números de paso son los del PDF *Paso a paso del Taller MLOps por rol*, y "(Guía: Paso X)" remite a la Guía del taller.

## Lo que necesitas saber

- **Eres dueño de:** `features.py`, `clustering.py`, `train.py`, `predict.py`, MLflow y el `champion`, `tests/test_api.py` y la justificación del modelo.
- **Datos:** `data/raw/gold_final.csv` (copia del Gold del ETL): 20 países. Columnas: `Country`, `Country_Code`, `Capital_City`, `Region`, `Income_Level`, `Longitude`, `Latitude`, `Energy_Consumption`, `Renewable_Energy`, `Energy_per_Renewable_Unit`, `Renewable_Share`, `Environmental_Status`.
- **Qué predice el modelo (D1):** el segmento que crea KMeans, no `Environmental_Status`. Esa columna es una regla sobre `Renewable_Share` (≥ 0,30 Green, ≥ 0,10 Moderate, resto Critical): se usa para **comparar** los segmentos, nunca como variable de entrada ni como target.
- **Contrato de `/predict` (D2):** entra `energy_consumption`, `renewable_energy` e `income_level`; sale `segment_id` y `segment_name`. La API solo llama a tu `predict_segment()`.
- **Nombres (D3):** modelo y experimento `green-data-segmentation`, alias `champion`, métrica **F1 macro**.
- **Ceremonias:** las facilita el Scrum Master (Francisco), que también revisa y hace merge de los PR. Tú participas en todas.

## Cuidado con los datos

- **Solo 20 filas.** El conjunto de prueba de un split normal serían 4–6 países, así que un F1 sobre eso no es confiable. Usa validación cruzada y reporta media ± desviación.
- **Circularidad.** Los segmentos salen de las mismas variables que el modelo luego predice, así que un F1 alto es esperable y no prueba generalización. Varios modelos pueden empatar en 1,0.
- **Valores extremos.** China (3000) y EE. UU. (1200) pueden quedar como segmentos de un solo país si no escalas bien.
- **`Low income`** no aparece en los datos; los otros tres niveles sí.

## Resumen

| Sprint | Pasos tuyos | Qué entregas | Qué esperas de otros |
|---|---|---|---|
| 1 | 9, 10, 11.1, 12, 13, 14 | Segmentos, runs en MLflow, `champion`, `predict_segment()` | DE: `config.py` y `load_data()`. PO: nombres de segmentos (paso 10) |
| 2 | 16, 17.3, 17.4 (features), 18, 22 | `test_api.py`, tests de `features.py` | DE: API (paso 17.1) |
| 3 | 24.3, 25, 27 | Capturas y justificación del modelo | — |

---

## Sprint 1 (24–28 nov)

Ruta crítica: **9 → 10 → 12 → 13 → 14**. El DE necesita tu paso 14 para el paso 17.1.

### Paso 9 — Features y segmentos (Guía: Paso 7)
Entrada: `load_data()` y `config.py` del DE (pasos 7.1 y 8.1).
- [ ] **`src/features.py`:**
  - función que calcula `Renewable_Share = renewable_energy / energy_consumption` (mismo criterio que el ETL: consumo 0 → indefinido);
  - mapeo ordinal de `income_level`: `Low income` 0, `Lower middle income` 1, `Upper middle income` 2, `High income` 3. Un valor fuera de la lista debe lanzar `ValueError`;
  - escalado dentro de un `Pipeline` de sklearn, de modo que entrenamiento y API usen exactamente la misma transformación.
  - Evita `Energy_per_Renewable_Unit` salvo que la necesites: el ETL la calcula con `+1` en el denominador y habría que replicarlo idéntico en la API.
- [ ] **`src/clustering.py`:** KMeans con `random_state` fijo y `n_init` explícito.
  - Punto de partida de variables: `energy_consumption`, `renewable_share` e `income_level` ordinal. Prueba con y sin `income_level` y con y sin `log1p` en el consumo.
  - Prueba varios `k` (por ejemplo 2 a 5). Para cada uno anota silhouette y tamaño de cada segmento.
  - Descarta los `k` con segmentos de menos de unos 4 países (rompen la validación estratificada).
  - Elige por silhouette y por interpretabilidad (lo valida el PO en el paso 10).
- [ ] Guardar la tabla de `k` probados con su silhouette y tamaños: sirve para la justificación del paso 24.3.

**Hecho cuando:** los 20 países tienen segmento, es reproducible y puedes justificar `k`.

### Paso 10 — Nombrar segmentos con el PO (Guía: Paso 7)
- [ ] Preparar para el PO: centroides **en unidades originales** (desescalados), lista de países por segmento y tabla cruzada segmento × `Environmental_Status`.
- [ ] Ajustar `k` o las variables si el PO rechaza un resultado.
- [ ] Con el nombre de cada segmento, agregar `SEGMENT_NAMES` (id → nombre) a `config.py` por PR. Si cambia el clustering, hay que regenerarlo: añade un test que falle si el número de segmentos no coincide con el de nombres.

### Paso 11.1 — Servidor de MLflow (Guía: Paso 8)
- [ ] Con el entorno virtual activo: `mlflow server --host 127.0.0.1 --port 5000` (o el comando de la Guía).
- [ ] Abrir `http://127.0.0.1:5000`. Deja esta terminal abierta mientras entrenas.

### Paso 12 — `src/train.py` (Guía: Paso 9)
- [ ] Tres modelos: Logistic Regression, Random Forest y Gradient Boosting. Cada uno un run de MLflow (mismo experimento) con parámetros y métricas.
- [ ] Evaluación: validación cruzada estratificada (por ejemplo 3 folds, con `random_state`), métrica `f1_macro`. Registrar media y desviación estándar.
- [ ] **Regla de desempate, definida antes de entrenar:** mayor F1 medio, luego menor desviación, luego el modelo más simple.
- [ ] Reentrenar el elegido con los 20 países (no sobran datos para reservar) y registrar el `Pipeline` completo: preprocesamiento + modelo.

**Hecho cuando:** MLflow muestra los 3 runs comparables.

### Paso 13 — Registrar el `champion` (Guía: Paso 10)
- [ ] Registrar el mejor modelo con el nombre `green-data-segmentation` y asignarle el alias `champion` (con `MlflowClient().set_registered_model_alias(...)` o desde la UI).
- [ ] Verificar: `mlflow.sklearn.load_model("models:/green-data-segmentation@champion")` carga sin errores y predice.

### Paso 14 — `src/predict.py` (Guía: Paso 11)
- [ ] `predict_segment(energy_consumption, renewable_energy, income_level)` devuelve `{"segment_id": ..., "segment_name": ...}`.
- [ ] Carga el `champion` una sola vez y lo reutiliza (la API lo llamará muchas veces).
- [ ] Probar con un caso de cada segmento (sirven de base para los tests).
- [ ] Avisar al DE: es su entrada para el paso 17.1.

**Hecho cuando:** la predicción local es correcta para un caso por segmento.

### Paso 15 — Review y Retro 1
- [ ] Mostrar en MLflow los 3 runs, el `champion` registrado y la predicción local.

---

## Sprint 2 (1–5 dic)

### Paso 16 — Sprint Planning 2 (facilita SM)

### Paso 17.3 — `tests/test_api.py` (Guía: Paso 20)
- [ ] Usar el `TestClient` de FastAPI (necesita `httpx`; confirma con el DE que esté en `requirements.txt`).
- [ ] Sustituir `predict_segment` por una versión simulada: los tests no pueden necesitar MLflow ni Docker para correr en el CI.
- [ ] Casos:
  - `/health` → 200;
  - `/predict` válido → 200 con `segment_id` y `segment_name`;
  - consumo 0 → 422;
  - renovable > consumo → 422;
  - falta un campo → 422;
  - `income_level` inexistente → 422;
  - `/metrics` → 200 y contiene los nombres de las métricas tras una predicción.

**Hecho cuando:** `pytest` pasa en una máquina limpia sin servicios externos.

### Paso 17.4 — Tests de `features.py` (Guía: Pasos 6–7)
- [ ] `Renewable_Share` con un caso conocido y consumo 0.
- [ ] Mapeo ordinal correcto y error con un nivel desconocido.
- [ ] El clustering es reproducible: dos corridas con el mismo `random_state` dan los mismos segmentos.
- [ ] El número de segmentos coincide con `SEGMENT_NAMES`.
- [ ] Los tests de `data.py` los escribe el DE.

### Paso 18 — Integrar API y `champion`, con el DE (Guía: Pasos 11–12)
- [ ] Con MLflow encendido, probar `/predict` en `http://localhost:8000/docs` con un caso de cada segmento.
- [ ] Si el modelo cargado no coincide con lo que predices localmente, revisar que el alias `champion` apunte a la versión correcta.

### Paso 22 — Review y Retro 2 (facilita SM)

---

## Sprint 3 (8–11 dic)

### Paso 24.3 — Capturas y justificación del modelo (Guía: Pasos 9–10)
- [ ] Capturas de MLflow: lista de runs, comparación de los 3 modelos y el modelo registrado con el alias `champion`.
- [ ] Documento corto con:
  - la tabla de los 3 modelos (F1 macro medio ± desviación);
  - la regla de desempate y por qué ganó el elegido;
  - la tabla de `k` probados (silhouette y tamaños);
  - **los límites, dichos con claridad:** solo 20 países y datos de laboratorio, y los segmentos salen de las mismas variables que el modelo predice, así que el F1 no demuestra capacidad de generalizar.

### Paso 25 — Prueba cruzada
- [ ] Correr todo en una máquina que no sea la tuya siguiendo solo el README. Corregir lo que falle.

### Paso 27 — Review final y Retro (facilita SM)
