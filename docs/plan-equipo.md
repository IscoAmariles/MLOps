# Plan de trabajo del equipo — MLOps Green Data

Plan para los tres roles del equipo: **Product Owner (PO)**, **Data Engineer (DE)** y **ML Engineer (MLE)**.
Usa como contexto y fuente de datos el repo `Laboratorio-MLOps-green-data-etl` (ETL con Arquitectura Medallion).

Sigue los 27 pasos del PDF *Paso a paso del Taller MLOps por rol*. La numeración de pasos y las referencias a la Guía son las de ese PDF. Los pasos se adaptan al dataset de este proyecto y a un equipo de tres personas.

| Sprint | Fechas (2026) | Pasos | Objetivo |
|---|---|---|---|
| 1 | 24–28 nov | 1–15 | Base del repo, datos y modelo registrado |
| 2 | 1–5 dic | 16–22 | API, Streamlit, monitoreo y CI |
| 3 | 8–11 dic | 23–27 | Cierre, documentación y demo |

**Planes por rol** (cada persona ejecuta el suyo; este documento es la vista general):

- [Product Owner](plan-product-owner.md)
- [Data Engineer](plan-data-engineer.md)
- [ML Engineer](plan-ml-engineer.md)

Si el equipo cambia una decisión de la sección 4, se actualiza aquí y en los tres planes.

---

## 1. Contexto: qué nos entrega el repo ETL

El ETL toma dos fuentes y las lleva por Bronze → Silver → Gold → Data Warehouse con Airflow 3.3.2 sobre WSL2 + Docker:

- API REST del World Bank (datos de países).
- `data/energy_consumption.csv` (20 países). Según el README del ETL son **datos de laboratorio, no estadísticas oficiales**.

**Nosotros consumimos la capa Gold:** `data/gold/gold_final.csv` (20 filas × 12 columnas, sin nulos).

| Columna | Descripción |
|---|---|
| `Country`, `Country_Code` | País y código ISO (clave de unión en el ETL) |
| `Capital_City`, `Region`, `Income_Level`, `Longitude`, `Latitude` | Atributos del World Bank |
| `Energy_Consumption`, `Renewable_Energy` | Datos de energía del CSV (el ETL no documenta unidades) |
| `Energy_per_Renewable_Unit` | `Energy_Consumption / (Renewable_Energy + 1)` |
| `Renewable_Share` | `Renewable_Energy / Energy_Consumption` (NaN si el consumo es 0) |
| `Environmental_Status` | Regla del ETL sobre `Renewable_Share`: ≥ 0,30 **Green**, ≥ 0,10 **Moderate**, resto **Critical** |

Lo que muestran los datos (verificado sobre `gold_final.csv`):

- `Environmental_Status`: Critical 9, Green 6, Moderate 5.
- `Energy_Consumption` va de 25 a 3000 y `Renewable_Energy` de 6 a 300. `Renewable_Share` va de 0,017 a 0,909. Hay valores extremos (China 3000, EE. UU. 1200).
- `Income_Level` solo tiene 3 de los 4 niveles del World Bank (High 10, Upper middle 7, Lower middle 3). No hay `Low income`.
- `Region` tiene 7 valores en 20 filas, varios con un solo país.

**Fuera de alcance:** modificar el repo ETL, usar Airflow, consultar el Postgres `warehouse-db` o volver a llamar a la API del World Bank.

---

## 2. Cómo se adapta el taller a este dataset

| Taller (Mall Customers) | Este proyecto |
|---|---|
| `Mall_Customers.csv` en `data/raw` | Copia de `gold_final.csv` del ETL en `data/raw` |
| 200 clientes | 20 países |
| `/predict`: gender, age, annual income, spending score | `/predict`: `energy_consumption`, `renewable_energy`, `income_level` (decisión D2) |
| KMeans genera segmentos y el PO les pone nombre | KMeans genera segmentos de países y el PO les pone nombre |
| Logistic Regression, Random Forest, Gradient Boosting; mejor F1 → `champion` | Igual, con F1 macro |
| `mall_customer_*_total` | `green_data_*_total` (decisión D4) |

---

## 3. Roles

| Rol | Foco | Es dueño de |
|---|---|---|
| **PO** | Valor de negocio y aceptación | Backlog y tablero, nombres de segmentos, Streamlit, prueba de aceptación, README (arquitectura) y guion de demo |
| **DE** | Datos, repo, infraestructura y observabilidad | Repo y CI, copia de datos, `config.py`, `data.py`, API, Docker Compose, Prometheus, Grafana |
| **MLE** | Modelo | `features.py`, `clustering.py`, `train.py`, MLflow, `champion`, `predict.py`, `test_api.py`, justificación del modelo |

El equipo no tiene Scrum Master. Sus tareas se reparten así: repo, CI y README base → DE; tablero → PO; `test_api.py` → MLE; facilitación de ceremonias rotativa (Sprint 1 y 3: DE, Sprint 2 y retro final: MLE). El PO acepta en cada Review.

**Acuerdos de trabajo**

- Cada persona trabaja en una rama propia y abre PR a `dev`. Otro rol aprueba el PR (DE ↔ MLE se revisan entre sí; el PO revisa lo que toque documentación y Streamlit).
- `main` solo recibe merges desde `dev` al cerrar cada sprint.
- Lo que necesite infraestructura (MLflow, Docker) se omite o se simula en los tests, para que el CI no dependa de ella. Es el mismo criterio que usa el ETL con `test_dag.py`, que se omite si Airflow no está instalado.

---

## 4. Decisiones para cerrar en el Sprint Planning 1 (paso 2)

Cada una trae una propuesta. Si el equipo está de acuerdo, se confirma y se registra en el README.

| # | Decisión | Propuesta | Por qué |
|---|---|---|---|
| D1 | Qué predice el modelo | Segmento de país creado con KMeans (pasos 9–10). `Environmental_Status` del ETL **no** es el target: se usa para comparar y validar los segmentos. | `Environmental_Status` es una regla sobre `Renewable_Share`. Si el modelo recibe consumo y renovable, solo aprendería esa regla (fuga de información) y su F1 no diría nada. |
| D2 | Contrato de `/predict` | Entrada: `energy_consumption` (> 0), `renewable_energy` (≥ 0 y ≤ `energy_consumption`), `income_level` (valores del World Bank, codificado como ordinal). Salida: `segment_id` y `segment_name`. Entradas inválidas → 422. | Pocas variables porque hay 20 filas. El consumo 0 daría `Renewable_Share` indefinido (el ETL lo trata como NaN). El PO confirma que renovable ≤ consumo es una regla de negocio válida. |
| D3 | Nombre del modelo y métrica | Modelo registrado y experimento: `green-data-segmentation`. Alias: `champion`. Métrica: F1 macro. | Las clases están desbalanceadas (9/6/5), por eso macro. |
| D4 | Nombres de métricas Prometheus | `green_data_prediction_count_total` y `green_data_segment_predictions_total` | Reemplazan a `mall_customer_*` del taller. Se decide ahora para que API, Prometheus y Grafana usen el mismo nombre desde el inicio. |
| D5 | Origen de los datos | Copia de `data/gold/gold_final.csv` (commit `684fba9` del ETL) en `data/raw/gold_final.csv`. | Así el proyecto corre sin Airflow, sin Postgres y sin red. Es necesario para la prueba cruzada (paso 25). |
| D6 | Unidades de energía | El PO consulta al autor del ETL qué unidades tienen `Energy_Consumption` y `Renewable_Energy`. | El ETL no las documenta y la pantalla de Streamlit las necesita. |

---

## 5. Plan por sprint

**Hecho:** las carpetas del repo (`src/`, `api/`, `app/`, `docker/`, `tests/`, `data/raw`, `data/monitoring`, `.github/workflows`, `docs/`) ya están creadas.

### Sprint 1 (24–28 nov): base y modelo

Ruta crítica: 5 → 7.1 → 8.1 → 9 → 10 → 12 → 13 → 14.

| Paso | Rol | Tarea | Hecho cuando |
|---|---|---|---|
| 1 | PO | Escribir el backlog como historias con criterios de aceptación (semilla en la sección 6) y montar el tablero. | Backlog priorizado y cada historia con criterios verificables. |
| 2 | Todos (facilita DE) | Sprint Planning 1: cerrar D1–D6 (Guía: Pasos 9–12). | Decisiones registradas en el README. |
| 3 | DE | Crear el repo en GitHub con ramas `main` y `dev` y proteger `main` (Guía: Paso 19, adelantado). | `main` no acepta push directo. |
| 4 | DE | Dejar `.gitignore`, `src/features.py` y `tests/test_api.py` como archivos base (Guía: Pasos 0–2). El `.gitignore` excluye `.venv/`, `__pycache__/`, `.env`, `mlruns/`, `mlartifacts/` y los CSV generados en `data/monitoring/`. | Estructura subida a `dev`. |
| 5 | DE | Copiar `gold_final.csv` a `data/raw/`, llenar `requirements.txt` (mismas versiones que el ETL: `pandas==2.3.2`, `numpy==2.3.2`) y subir todo (Guía: Pasos 3–4). Anotar en el README el commit de origen. | El archivo está en `data/raw` y el origen está documentado. |
| 6 | Todos | Clonar, crear el entorno virtual e instalar dependencias (Guía: Pasos 1 y 4). Acordar una misma versión de Python (el ETL declara 3.12). | Los tres tienen el entorno funcionando. |
| 7.1 | DE | `src/config.py` con rutas y parámetros (Guía: Paso 5). Reutilizar el patrón del `config.py` del ETL: `pathlib` y variable `PROJECT_DIR`, sin rutas de Windows. Incluir nombre del modelo, alias, experimento, `random_state` y la URI de MLflow. | Todos los módulos importan sus rutas desde `config.py`. |
| 7.2 | DE | `docker/prometheus.yml` (Guía: Paso 15). La API corre en el host y Prometheus en Docker, así que el *target* es `host.docker.internal:8000`. | Archivo listo para el compose. |
| 7.3 | PO | Explorar el Gold y bocetar la pantalla de Streamlit (Guía: Pasos 3 y 13). El boceto incluye el aviso "datos de laboratorio". | Boceto con campos de entrada, resultado y aviso. |
| 8.1 | DE | `src/data.py`: cargar `data/raw/gold_final.csv` y validar (columnas esperadas, 20 filas, sin nulos, `Country_Code` único). Mismo estilo que `validate_bronze` del ETL (`FileNotFoundError` / `ValueError`) (Guía: Paso 6). | `load_data()` funciona y falla con mensaje claro si el archivo está mal. |
| 8.2 | DE | `docker-compose.yml` con Prometheus. `docker compose up -d` (Guía: Pasos 16–17). | Prometheus abre en `localhost:9090`. |
| 9 | MLE | `src/features.py` y `src/clustering.py`. Derivar `Renewable_Share`, escalar dentro de un `Pipeline` de sklearn y generar segmentos con KMeans (Guía: Paso 7). Elegir `k` con silhouette y exigir un tamaño mínimo por segmento (unos 4 países). | Los 20 países tienen segmento, reproducible con `random_state` fijo, y `k` justificado. |
| 10 | PO + MLE | Revisar centroides y nombrar los segmentos (Guía: Paso 7). Cruzar los segmentos con `Environmental_Status`. Hipótesis a validar, no a asumir: un grupo de grandes consumidores con poca renovable (p. ej. China, EE. UU., India), uno de líderes renovables (p. ej. Noruega, Uruguay, Kenia) y uno intermedio. | Cada segmento tiene nombre de negocio y una frase de descripción, aprobados por el PO. |
| 11.1 | MLE | Levantar MLflow en `127.0.0.1:5000` (Guía: Paso 8). | La UI abre. |
| 11.2 | DE | `api/main.py` base con `/health` y el esquema de D2 con sus reglas de validación (Guía: Paso 12, parcial). | `localhost:8000/docs` muestra el esquema y las entradas inválidas devuelven 422. |
| 11.3 | DE | Borrador del README con la instalación y revisión de PR abiertos (Guía: Paso 19). | README con pasos de instalación. |
| 12 | MLE | `src/train.py`: Logistic Regression, Random Forest y Gradient Boosting, un run de MLflow cada uno con parámetros y F1 macro (Guía: Paso 9). Con 20 filas el conjunto de prueba tendría solo 4–6 países, así que usar validación cruzada estratificada y reportar media ± desviación. | 3 runs comparables en MLflow. |
| 13 | MLE | Registrar el mejor por F1 con el alias `champion` (Guía: Paso 10). Registrar el `Pipeline` completo (preprocesamiento + modelo) para que la API no reimplemente el escalado. | `models:/green-data-segmentation@champion` se carga sin errores. |
| 14 | MLE | `src/predict.py` con `predict_segment(energy_consumption, renewable_energy, income_level)` que devuelve id y nombre del segmento (Guía: Paso 11). | Predicción local correcta para un caso de prueba por segmento. |
| 15 | Todos (facilita DE, acepta PO) | Sprint Review y Retro 1 (Guía: Pasos 8–11). | MLflow muestra los 3 runs y `champion` registrado. |

### Sprint 2 (1–5 dic): servicio y monitoreo

Ruta crítica: 14 → 17.1 → 18 → 19 → 20.1 → 21 → 22.

| Paso | Rol | Tarea | Hecho cuando |
|---|---|---|---|
| 16 | Todos (facilita MLE) | Sprint Planning 2 (Guía: Pasos 12–20). | Compromisos del sprint acordados. |
| 17.1 | DE | Completar la API: `/predict` (llama a `predict_segment`), `/metrics`, contadores de Prometheus (D4) y log de predicciones (Guía: Paso 12). | Cada `/predict` suma al contador y agrega una fila a `data/monitoring/api_predictions_log.csv`. |
| 17.2 | PO | `app/streamlit_app.py`: formulario con los 3 campos, nombre del segmento como resultado y aviso de datos de laboratorio (Guía: Paso 13). Puede avanzar contra el contrato D2 antes de que exista el `champion`. | La pantalla llama a la API y muestra el segmento. |
| 17.3 | MLE | `tests/test_api.py`: `/health`, `/predict` válido y entradas inválidas → 422 (Guía: Paso 20). Con modelo simulado, sin MLflow ni Docker. | Los tests pasan en una máquina limpia. |
| 17.4 | DE + MLE | Tests de `src/` (Guía: Pasos 6–7). DE: `data.py` (archivo faltante, columnas, nulos). MLE: `features.py` (casos como consumo 0). | `pytest` pasa completo. |
| 18 | DE + MLE | Integrar la API con el `champion` y probar `/predict` en `localhost:8000/docs` (Guía: Pasos 11–12). | Respuesta correcta con el modelo real. |
| 19 | PO | Prueba de aceptación con 3 terminales: MLflow, API y Streamlit (Guía: Paso 14). Hacer una predicción por segmento. | El log tiene 3 filas nuevas. |
| 20.1 | DE | Consultar `green_data_prediction_count_total` y `green_data_segment_predictions_total` en Prometheus (Guía: Paso 17). | Ambas métricas devuelven valores tras las predicciones. |
| 20.2 | DE | `.github/workflows/ci.yml`: instalar dependencias y correr `pytest` (Guía: Paso 20). | Corre en cada push. |
| 21 | DE | Conectar Grafana a `http://prometheus:9090` y crear el dashboard con las consultas del taller (Guía: Paso 18). | El dashboard muestra las dos métricas. |
| 22 | Todos (facilita MLE, acepta PO) | Sprint Review y Retro 2 (Guía: Pasos 12–18). | Una predicción hecha desde Streamlit aparece en Grafana. |

### Sprint 3 (8–11 dic): cierre y demo

Ruta crítica: 24.2 → 25 → 26.

| Paso | Rol | Tarea | Hecho cuando |
|---|---|---|---|
| 23 | Todos (facilita DE) | Sprint Planning 3 (Guía: Pasos 19–20). | Compromisos del sprint acordados. |
| 24.1 | PO | Completar el README con la arquitectura y el orden para correr todo; escribir el guion de la demo (Guía: Paso 19). | Alguien ajeno al equipo puede arrancar el proyecto solo con el README. |
| 24.2 | DE | Dejar el CI en verde y crear un tag de versión (Guía: Pasos 19–20). | Tag publicado sobre un commit con CI verde. |
| 24.3 | MLE | Capturas de MLflow y justificación del modelo elegido (Guía: Pasos 9–10). Debe decir con franqueza que hay solo 20 países y que los segmentos salen de las mismas variables que el modelo predice. | Documento con capturas y justificación. |
| 24.4 | DE | Exportar el dashboard de Grafana a JSON y subirlo al repo, por ejemplo en `docker/` (Guía: Paso 18). | El JSON importa bien en un Grafana limpio. |
| 25 | Todos | Prueba cruzada: cada uno corre el proyecto completo en una máquina que no es la suya y corrige lo que falle (Guía: Pasos 0–18). No hace falta el ETL ni Airflow gracias a D5. | Los tres corren todo solo con el README. |
| 26 | DE organiza, PO presenta | Ensayo de la demo (Guía: Paso 14). | Demo completa sin intervenciones fuera de guion. |
| 27 | Todos (facilita MLE, acepta PO) | Review final y Retro del proyecto. | Backlog aceptado por el PO. |

---

## 6. Semilla del backlog (paso 1, PO)

Punto de partida; el PO ajusta redacción y prioridad.

1. **Consultar el segmento de un país.** Como analista, quiero ingresar consumo, energía renovable y nivel de ingreso para saber a qué segmento pertenece. *Aceptación:* formulario con 3 campos; muestra el nombre del segmento; un error claro si `energy_consumption` ≤ 0 o `renewable_energy` > `energy_consumption`.
2. **Entender los segmentos.** Como analista, quiero un nombre y una descripción por segmento para interpretar el resultado. *Aceptación:* los segmentos están nombrados y descritos; el PO aprobó el cruce con `Environmental_Status`.
3. **Comparar modelos.** Como equipo, quiero ver en MLflow tres modelos comparables por F1 macro y uno registrado como `champion`. *Aceptación:* 3 runs visibles y alias `champion` cargable.
4. **Monitorear el uso.** Como operador, quiero ver cuántas predicciones se hacen y por segmento. *Aceptación:* una predicción desde Streamlit aparece en Grafana y en `api_predictions_log.csv`.
5. **Confiar en los cambios.** Como equipo, quiero que cada push corra los tests. *Aceptación:* `ci.yml` corre en cada push y está en verde al cierre.
6. **Reproducir el proyecto.** Como equipo, quiero correr todo en otra máquina siguiendo el README. *Aceptación:* prueba cruzada exitosa de los tres integrantes.

---

## 7. Entregas entre roles

| De → A | Qué | Pasos |
|---|---|---|
| DE → todos | `config.py`, copia de datos y `data.py` (`load_data()`) | 5, 7.1, 8.1 → 9 |
| DE → todos | Compose con Prometheus en `localhost:9090` | 8.2 → 20.1 |
| PO → MLE | Nombres de segmento (salen en `predict.py` y en la API) | 10 → 14, 17.1 |
| MLE → DE | `predict_segment()` y el alias `champion` | 14 → 17.1, 18 |
| DE → PO | Esquema D2 y `/health` en la API | 11.2 → 17.2 |
| DE + MLE → PO | API con el modelo real | 18 → 19 |

---

## 8. Riesgos y qué hacer

| Riesgo | Mitigación |
|---|---|
| **Solo 20 filas.** Un F1 sobre 4–6 países de prueba no es estadísticamente confiable. | Validación cruzada estratificada, reportar media ± desviación y no presentar el F1 como evidencia de generalización. El valor del proyecto es el flujo MLOps. |
| **Circularidad.** Los segmentos se crean con las mismas variables que luego predice el modelo, así que un F1 alto es esperable. | Decirlo en la justificación (24.3). |
| **Valores extremos y escala.** China (3000) y EE. UU. (1200) pueden formar segmentos de un solo país. | Estandarizar dentro del `Pipeline` (así entrenamiento y API usan la misma transformación), probar `log1p` o un `k` menor, y exigir un tamaño mínimo por segmento. |
| **Un segmento con un solo país** rompe la validación estratificada. | Se previene con el tamaño mínimo del paso 9. |
| **Consumo 0 o renovable > consumo.** | La API devuelve 422 (D2). |
| **`Low income` no está en los datos.** El modelo nunca lo vio. | Aceptarlo como ordinal más bajo y documentarlo en el README. |
| **Datos de laboratorio, no oficiales.** | Aviso visible en Streamlit y en el README. |
| **Recursos de Docker Desktop.** El stack de Airflow del ETL son 8 servicios (mínimo 4 GB de RAM). Sus puertos 8080, 5555 y 5433 no chocan con 5000, 8000 y 9090. | Hacer `docker compose down` del ETL mientras se trabaja en este proyecto. |
| **El CI depende de infraestructura.** | Tests con modelo simulado, sin MLflow ni Docker (17.3). |
