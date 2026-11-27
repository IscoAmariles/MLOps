# Acta de Revisión Previa a Presentación Cliente

## Proyecto

MLOps Green Data

## Responsable

Andrés Fernando López Rendón

Product Owner

## Fecha

23/11/2026

---

# Objetivo

Validar los entregables comprometidos para la Review 1 antes de la presentación formal al cliente.

---

# 1. Backlog y Tablero

## Validación

✅ APROBADO CONDICIONALMENTE

Se requiere verificar:

- Historias en formato:
  - Como...
  - Quiero...
  - Para...

- Criterios de aceptación verificables.

- Priorización por sprint.

- Publicación del enlace del tablero.

Observación:

El enlace del tablero debe compartirse con todo el equipo antes de la Review.

---

# 2. Decisiones del Sprint Planning

## D2

✅ APROBADA

Se confirma que:

- Energy_Consumption debe ser mayor que cero.
- Renewable_Energy no puede superar Energy_Consumption.

Las violaciones deberán generar error HTTP 422.

---

## D6

⚠ PENDIENTE DOCUMENTACIÓN

El ETL original no documenta unidades para:

- Energy_Consumption
- Renewable_Energy

Mientras no exista validación oficial, deberá mostrarse en Streamlit:

"Datos de laboratorio, no estadísticas oficiales."

---

# 3. Boceto Streamlit

## Validación

✅ APROBADO

El diseño debe incluir:

- Campo Energy Consumption.
- Campo Renewable Energy.
- Campo Income Level.
- Botón Consultar.
- Nombre del segmento.
- Descripción del segmento.
- Mensajes de error.
- Aviso de datos de laboratorio.

---

# 4. Segmentos

## Propuesta revisada

### Segmento 0

✅ APROBADO

Grandes consumidores poco renovables

Ejemplos:

China, Estados Unidos, India, Alemania, Japón, Brasil, Canadá y Francia.

---

### Segmento 1

✅ APROBADO

Transición intermedia

Ejemplos:

Colombia, México, España, Australia, Argentina, Chile, Perú, Egipto y Sudáfrica.

---

### Segmento 2

✅ APROBADO

Líderes renovables

Ejemplos:

Noruega, Uruguay y Kenia.

---

# 5. Entorno

## Validación

✅ APROBADO

Requisitos:

- Python 3.12.
- Git.
- Docker Desktop.
- requirements.txt instalado correctamente.

---

# Checklist para Aceptación Sprint 1

Antes de aceptar el sprint deberá comprobarse:

- MLflow operativo.
- Modelo champion registrado.
- Predicciones válidas para cada segmento.
- Prometheus accesible.
- API accesible mediante /docs.
- Validación correcta de entradas inválidas.

---

# Concepto Final

✅ REVISIÓN FAVORABLE

El proyecto presenta una base sólida para continuar hacia la Review 1.

Se recomienda completar la documentación pendiente relacionada con D6 antes de la presentación formal al cliente.

---

Andrés Fernando López Rendón

Product Owner
