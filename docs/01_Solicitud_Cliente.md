# Solicitud del Cliente

## Proyecto

Green Data Segmentation Platform

## Cliente

Área de Analítica Ambiental y Sostenibilidad

## Contexto

La organización requiere una solución tecnológica que permita clasificar países según sus características energéticas utilizando técnicas de Machine Learning.

Actualmente se dispone de un dataset consolidado proveniente de un proceso ETL que contiene información sobre consumo energético, energía renovable y nivel de ingresos para un conjunto de países.

Se requiere transformar esta información en un servicio capaz de realizar predicciones automatizadas y accesibles para usuarios no técnicos.

---

# Necesidad del Negocio

Se requiere una plataforma capaz de:

- Clasificar países en segmentos de comportamiento energético.
- Exponer las predicciones mediante una API.
- Permitir consultas desde una interfaz web intuitiva.
- Registrar las predicciones realizadas.
- Monitorear el servicio mediante métricas operativas.
- Mantener trazabilidad del ciclo de vida del modelo.

---

# Requerimientos Funcionales

## RF-01

Permitir el ingreso de:

- Consumo energético.
- Energía renovable.
- Nivel de ingreso.

## RF-02

Determinar automáticamente el segmento correspondiente.

## RF-03

Mostrar una descripción clara del segmento identificado.

## RF-04

Validar entradas incorrectas.

## RF-05

Registrar las predicciones generadas.

## RF-06

Visualizar indicadores operativos del servicio.

---

# Requerimientos Técnicos

- Python 3.12.
- FastAPI.
- Streamlit.
- MLflow.
- Prometheus.
- Grafana.
- Docker.

---

# Resultado Esperado

Contar con una solución funcional que permita segmentar países utilizando Machine Learning, manteniendo trazabilidad, monitoreo y facilidad de uso para usuarios finales.