# Bitácora 03 · Seguimiento y decisiones · Scrum Master · Sprint 1

**Proyecto:** MLOps Green Data  
**Fecha:** 2026-11-26  
**Rol:** Scrum Master (SM)  
**Iniciales:** FJAJ  
**Sprint:** 1 (24–28 nov) · Base del repo, datos y modelo registrado  
**Referencia:** los 27 pasos del PDF *Paso a paso del Taller MLOps por rol* y los [planes del equipo](../plan-equipo.md)

## 1. Objetivo

Revisar el estado de `main` después de los PR #2 a #6 contra los pasos del Sprint 1, comunicar a cada rol sus pendientes y dejar registradas las decisiones de proceso del equipo.

## 2. Decisiones del equipo

| Decisión | Detalle | Motivo |
|---|---|---|
| El equipo tiene 4 roles | PO: Andres (`AndreLopezRendon`). SM: Francisco (`IscoAmariles`). DE: Majo (`MajoGGezz`). MLE: Jean (`jean-h-e`). | El plan original se escribió para 3 roles sin SM. |
| Tareas del SM | El SM facilita todas las ceremonias (pasos 2, 15, 16, 22, 23 y 27), organiza el ensayo de la demo (paso 26), revisa y hace merge de los PR y lleva esta bitácora. | Repo, CI, README base y tag se quedan con el DE; el tablero con el PO; `test_api.py` con el MLE, como ya estaban repartidos. |
| PR directo a `main` | La rama `dev` existe, pero es opcional. | Proyecto de asignatura: no hace falta una rama de integración. |
| `main` no se protege | El paso 3 del PDF lo pide; el equipo decide no hacerlo. | Proyecto de asignatura, y el SM revisa cada PR antes del merge. |
| D6 la resuelve el PO | El PO es el autor del repo ETL, así que define él mismo las unidades de energía. | — |

Los planes del equipo y por rol quedan actualizados con estas decisiones.

## 3. Estado del Sprint 1 al 26 nov

**Hechos, con evidencia en `main`:** pasos 4, 5, 7.1, 7.2, 8.1, 9, 11.1, 11.2, 12, 13 y 14. El `champion` es Logistic Regression, con F1 macro de 0,962 ± 0,054 en validación cruzada de 3 folds.

| Paso | Rol | Estado | Qué falta |
|---|---|---|---|
| 1 Backlog y tablero | PO | Sin evidencia | Historias con criterios de aceptación y link del tablero |
| 2 Sprint Planning 1 | Todos (facilita SM) | Pendiente | Confirmar D1–D6 (D6 abierta) y registrarlas en el README |
| 3 Repo | DE | Hecho | `main` sin proteger por decisión del equipo |
| 6 Entornos | Todos | Parcial | DE y MLE con Python 3.12; falta confirmar el PO |
| 7.3 Boceto de Streamlit | PO | Sin evidencia | — |
| 8.2 Prometheus | DE | Parcial | Levantarlo y abrir `localhost:9090` |
| 10 Nombres de segmentos | PO + MLE | Parcial | Propuesta del MLE en `src/config.py`; falta la aprobación del PO |
| 11.3 README y revisión de PR | DE + SM | Parcial | README hecho; solo el PR #2 tiene revisión registrada |
| 15 Review y Retro 1 | Todos (facilita SM) | Pendiente | Antes del 28 nov |

**Pruebas:** `pytest` en `main` da 32 pasan y 3 omitidos (los de integración con MLflow). Una instalación limpia con `pip install -r requirements.txt` funciona.

## 4. Hallazgos

1. **Los tests de la API (paso 17.3) no llegaron a `main`.** El PR #5 se fusionó en `mle/sprint1-modelo` 15 segundos después de que el PR #4 ya se había fusionado en `dev`, y el commit `354fce4` quedó solo en las ramas del MLE. Probados contra la API actual: 9 pasan y 3 quedan en `xfail` hasta el paso 17.1.
2. **El `champion` solo existe en el MLflow local del MLE.** El README no explica cómo levantar MLflow ni cómo entrenar, así que nadie más puede reproducir el modelo para la Review, el paso 19 o la prueba cruzada (paso 25).
3. **Revisión de PR.** Del #3 al #6 no hay revisión registrada en GitHub. Desde ahora el SM deja un comentario o una aprobación en cada PR.
4. **Ajustes del review del PR #2 que siguen pendientes:** niveles de ingreso repetidos en `api/main.py` y `config.py`, tabla D1–D6 marcada como "Resultado" en el README y el pendiente de "cambiar la base a `dev`" en la bitácora 01.

## 5. Pendientes comunicados por rol

Se enviaron por el grupo del equipo el 26 nov.

| Rol | Pendientes |
|---|---|
| PO | Backlog y tablero (1), D6 y reglas de D2 (2), boceto de Streamlit (7.3), aprobar los nombres de los segmentos (10) y entorno con Python 3.12 (6) |
| DE | Prometheus en vivo (8.2), ajustes del review del PR #2 y, para el Sprint 2, subir lo preparado: API completa (17.1), tests de `data.py` (17.4), CI (20.2) y Grafana (21) |
| MLE | PR con los tests de la API (17.3), comandos de MLflow y entrenamiento en el README, tabla de segmentos para el PO (10), demo de MLflow para la Review 1 y estado de la bitácora 02 |

## 6. Próximos pasos del SM

1. Facilitar un Sprint Planning 1 corto para cerrar D1–D6.
2. Agendar y facilitar la Review y Retro 1 antes del 28 nov, con el MLE presente para mostrar MLflow.
3. Revisar y hacer merge de los PR que lleguen, con la revisión registrada en GitHub.
4. Registrar en esta bitácora el acta del Planning 1 y de la Review y Retro 1.
