# Propuesta del Equipo

## Proyecto

MLOps Green Data

## Responsable

Andrés Fernando López Rendón

Product Owner

---

# Objetivo General

Desarrollar una solución MLOps que permita predecir el segmento energético de un país a partir de su consumo energético, energía renovable y nivel de ingreso, garantizando trazabilidad, monitoreo y facilidad de uso mediante una interfaz web.

---

# Objetivos Específicos

1. Integrar datos provenientes de la capa Gold del proyecto Green Data ETL.

2. Entrenar y registrar modelos de segmentación en MLflow.

3. Exponer el modelo mediante una API REST desarrollada en FastAPI.

4. Implementar una interfaz de usuario mediante Streamlit.

5. Monitorear predicciones mediante Prometheus y Grafana.

6. Mantener registro histórico de predicciones.

---

# Decisiones de Negocio

## D1

El modelo predice segmentos energéticos.

No predice Environmental_Status.

---

## D2

Reglas de validación:

- Energy_Consumption > 0
- Renewable_Energy >= 0
- Renewable_Energy <= Energy_Consumption

Entradas inválidas retornarán HTTP 422.

---

## D3

Modelo oficial:

green-data-segmentation

Métrica principal:

F1 Macro

---

## D4

Monitoreo obligatorio mediante:

- Prometheus
- Grafana

---

## D5

La fuente oficial de datos será:

gold_final.csv

Origen:

Green Data ETL

Commit:

684fba9

---

## D6

Las unidades de energía no se encuentran documentadas en el ETL original.

Por lo tanto la solución deberá mostrar de forma visible:

"Datos de laboratorio. No corresponden a estadísticas oficiales."

---

# Segmentos Aprobados

## Segmento 0

Grandes consumidores poco renovables

Descripción:

Países con alto consumo energético y baja participación renovable.

---

## Segmento 1

Transición intermedia

Descripción:

Países con características energéticas intermedias y oportunidades de mejora en sostenibilidad.

---

## Segmento 2

Líderes renovables

Descripción:

Países con una alta participación de energía renovable respecto a su consumo.

---

# Concepto

La propuesta cubre los requerimientos funcionales y técnicos definidos por el cliente y se considera apta para iniciar el desarrollo.

---

Andrés Fernando López Rendón

Product Owner