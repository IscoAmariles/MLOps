# Plan del Product Owner (PO)

Tu parte del [plan del equipo](plan-equipo.md). Los números de paso son los del PDF *Paso a paso del Taller MLOps por rol*, y "(Guía: Paso X)" remite a la Guía del taller.

## Lo que necesitas saber

- **Qué construimos:** un servicio que dice a qué segmento pertenece un país según su consumo de energía y su energía renovable. Los datos salen del repo ETL (capa Gold): **20 países, datos de laboratorio, no estadísticas oficiales**.
- **Los segmentos** los crea KMeans (los calcula el MLE) y **tú los nombras** en el paso 10. El modelo predice el segmento; no predice `Environmental_Status` (decisión D1 del plan del equipo).
- **Contrato propuesto de `/predict` (D2):**
  - Entrada: `energy_consumption` (> 0), `renewable_energy` (≥ 0 y ≤ `energy_consumption`), `income_level` (`Low income`, `Lower middle income`, `Upper middle income` o `High income`).
  - Salida: `segment_id` y `segment_name`.
  - Entrada inválida: error 422.
- **Qué decides tú:** aceptas o rechazas en cada Review, confirmas las reglas de negocio y apruebas los nombres de los segmentos.
- **Ceremonias:** participas en las 6. Las facilita el Scrum Master (Francisco); tú aceptas en las Reviews (pasos 15, 22 y 27).

## Resumen

| Sprint | Pasos tuyos | Qué entregas | Qué esperas de otros |
|---|---|---|---|
| 1 | 1, 2, 7.3, 10, 15 | Backlog y tablero, decisiones D2/D6, boceto de pantalla, nombres de segmentos | DE: datos en `data/raw` (paso 5). MLE: centroides y segmentos (paso 9) |
| 2 | 16, 17.2, 19, 22 | `streamlit_app.py` y prueba de aceptación | DE: API con `/health` y esquema (paso 11.2). DE + MLE: API con el modelo real (paso 18) |
| 3 | 23, 24.1, 25, 26, 27 | README (arquitectura y orden de arranque) y guion de demo | DE y MLE: todo corriendo y documentado |

---

## Sprint 1 (24–28 nov)

### Paso 1 — Backlog y tablero
- [ ] Montar el tablero con columnas: Backlog, Sprint, En curso, En revisión, Hecho.
- [ ] Escribir las historias a partir de la [semilla del backlog](plan-equipo.md#6-semilla-del-backlog-paso-1-po) con el formato "Como… quiero… para…" y criterios de aceptación verificables. Puedes usar como base la columna "Hecho cuando" de los planes por rol.
- [ ] Priorizar y asignar cada historia a un sprint.

**Hecho cuando:** el backlog está priorizado y toda historia tiene criterios que otra persona puede comprobar.

### Paso 2 — Sprint Planning 1 (facilita SM)
Llevas estas tres cosas a la reunión:
- [ ] **D6 (unidades):** definir qué unidades tienen `Energy_Consumption` y `Renewable_Energy`. Eres el autor del repo ETL, pero allí no quedaron documentadas y la pantalla las necesita.
- [ ] **D2 (reglas):** confirmar que `energy_consumption` debe ser > 0 y que `renewable_energy` no puede superar a `energy_consumption`.
- [ ] **D1:** aceptar que el modelo predice segmentos y no `Environmental_Status`.

**Hecho cuando:** D1–D6 quedaron confirmadas o ajustadas y registradas en el README.

### Paso 7.3 — Explorar el Gold y bocetar Streamlit (Guía: Pasos 3 y 13)
- [ ] Abrir `data/raw/gold_final.csv` (el DE lo copia en el paso 5) y mirar: rangos de consumo y renovable, valores extremos (China 3000, EE. UU. 1200) y qué países clasifica el ETL como Green, Moderate y Critical.
- [ ] Bocetar la pantalla:
  - tres campos de entrada (el nivel de ingreso como lista con los 4 valores);
  - botón de consultar;
  - resultado con el nombre del segmento y su descripción;
  - mensajes de error comprensibles;
  - aviso visible: "datos de laboratorio, no estadísticas oficiales".

**Hecho cuando:** hay un boceto con campos, resultado, errores y aviso.

### Paso 10 — Nombrar los segmentos, con el MLE (Guía: Paso 7)
- [ ] Pedir al MLE: centroides **en unidades originales** (no escaladas), la lista de países por segmento y una tabla que cruce segmento contra `Environmental_Status`.
- [ ] Ponerle nombre de negocio a cada segmento y una frase de descripción. Hipótesis para contrastar, no para asumir: grandes consumidores con poca renovable (p. ej. China, EE. UU., India), líderes renovables (p. ej. Noruega, Uruguay, Kenia) y un grupo intermedio.
- [ ] Rechazar un resultado que no se pueda explicar a un analista no técnico, por ejemplo un segmento de un solo país. Pide al MLE que reajuste.
- [ ] Entregar la tabla al MLE (la usa `predict.py`) y quedártela para Streamlit.

| id | Nombre | Descripción (una frase) | Países de ejemplo |
|---|---|---|---|
| 0 | | | |
| 1 | | | |
| 2 | | | |

**Hecho cuando:** cada segmento tiene nombre y descripción aprobados por ti.

### Paso 15 — Review y Retro 1 (aceptas)
Aceptas el sprint si compruebas esto:
- [ ] MLflow (`127.0.0.1:5000`) muestra los 3 runs y el modelo `green-data-segmentation` con el alias `champion`.
- [ ] El MLE hace una predicción local correcta para un caso de cada segmento.
- [ ] Prometheus abre en `localhost:9090`.
- [ ] `localhost:8000/docs` muestra el esquema de `/predict` y rechaza entradas inválidas.

---

## Sprint 2 (1–5 dic)

### Paso 16 — Sprint Planning 2 (facilita SM)
- [ ] Revisar el backlog restante y confirmar el alcance del sprint.

### Paso 17.2 — `app/streamlit_app.py` (Guía: Paso 13)
- [ ] Construir el formulario del boceto: 3 campos y botón.
- [ ] Llamar a `POST http://127.0.0.1:8000/predict` y mostrar `segment_name` con su descripción.
- [ ] Mostrar mensajes claros cuando la API responde 422 y cuando no está disponible.
- [ ] Incluir el aviso de datos de laboratorio y las unidades (D6).
- [ ] Dejar la URL de la API como constante al inicio del archivo.
- [ ] Pedir al DE que `streamlit` y `requests` estén en `requirements.txt`.
- [ ] Puedes avanzar sin esperar al modelo: el contrato D2 ya está fijado y `/health` y el esquema existen desde el paso 11.2. Mientras no haya `/predict`, simula la respuesta.
- [ ] Ejecutar con `streamlit run app/streamlit_app.py` y abrir una PR a `main`.

**Hecho cuando:** la pantalla consulta la API y muestra el segmento.

### Paso 19 — Prueba de aceptación del flujo completo (Guía: Paso 14)
Con el entorno virtual activo y desde la raíz del repo, abre 3 terminales:

| Terminal | Comando |
|---|---|
| 1 — MLflow | `mlflow server --host 127.0.0.1 --port 5000` |
| 2 — API | `uvicorn api.main:app --port 8000` |
| 3 — Streamlit | `streamlit run app/streamlit_app.py` |

(Si el comando exacto cambia en la Guía, usa el de la Guía.)

Prueba estos casos. El segmento esperado lo completas tras el paso 10:

| Caso | `energy_consumption` | `renewable_energy` | `income_level` | Esperado |
|---|---|---|---|---|
| Noruega | 220 | 200 | High income | |
| EE. UU. | 1200 | 20 | High income | |
| Colombia | 250 | 35 | Upper middle income | |
| Consumo 0 | 0 | 0 | High income | Error claro, sin fila en el log |
| Renovable > consumo | 100 | 150 | High income | Error claro, sin fila en el log |

- [ ] Los 3 casos válidos devuelven el segmento esperado.
- [ ] `data/monitoring/api_predictions_log.csv` tiene **una fila nueva por cada predicción válida** y ninguna por las inválidas.
- [ ] Registrar cada fallo como incidencia en el tablero y asignarla.

**Hecho cuando:** los casos válidos pasan, los inválidos fallan con un mensaje claro y el log se llena.

### Paso 22 — Review y Retro 2 (facilita SM, aceptas)
- [ ] Hacer una predicción desde Streamlit y comprobar que **aparece en Grafana** (contador total y gráfico por segmento). Puede tardar unos segundos según el intervalo de scrape de Prometheus.
- [ ] Comprobar que el CI de GitHub está corriendo en cada push.

---

## Sprint 3 (8–11 dic)

### Paso 23 — Sprint Planning 3 (facilita SM)
- [ ] Acordar el alcance de cierre: README, guion, prueba cruzada y ensayo.

### Paso 24.1 — README final y guion de demo (Guía: Paso 19)
El DE deja el borrador con la instalación (paso 11.3). Tú lo completas:
- [ ] **Qué es** el proyecto y el aviso de datos de laboratorio.
- [ ] **Arquitectura:** repo ETL → copia del Gold en `data/raw` → clustering y entrenamiento con MLflow → `champion` → API → Streamlit; la API a Prometheus → Grafana; y el log CSV.
- [ ] **Orden para correr todo:** `docker compose up -d` (Prometheus y Grafana), luego MLflow, API y Streamlit.
- [ ] **Decisiones D1–D6** y el origen de los datos (commit `684fba9` del ETL).
- [ ] **Guion de demo.** Propuesta de orden:
  1. El problema y los datos.
  2. MLflow: los 3 runs y por qué ese `champion`.
  3. Streamlit: 3 predicciones (una por segmento) y una entrada inválida.
  4. Log, Prometheus y Grafana.
  5. CI en verde y tag.
  6. Límites: 20 países, datos de laboratorio.

**Hecho cuando:** alguien ajeno al equipo arranca el proyecto solo con el README.

### Paso 25 — Prueba cruzada
- [ ] Clonar el repo en una máquina que no sea la tuya y correr todo solo con el README. No hace falta el ETL ni Airflow.
- [ ] Anotar cada paso que falle o falte y corregirlo en el README o abrir incidencia.

### Paso 26 — Ensayo de la demo (organiza SM; tú presentas)
- [ ] Presentar siguiendo el guion y cronometrar.
- [ ] Anotar los tropiezos y ajustar el guion.

### Paso 27 — Review final y Retro (facilita SM, aceptas)
- [ ] Repasar el backlog completo contra los criterios de aceptación y aceptar o rechazar cada historia.
