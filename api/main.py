"""API de segmentación Green Data (paso 11.2, base).

Ejecutar desde la raíz del repo:
    uvicorn api.main:app --port 8000
Documentación interactiva: http://localhost:8000/docs
"""

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

app = FastAPI(
    title="Green Data Segmentation API",
    description="Predice el segmento de un país a partir de su consumo de energía, "
    "su energía renovable y su nivel de ingreso. Datos de laboratorio, no oficiales.",
    version="0.1.0",
)

IncomeLevel = Literal[
    "Low income",
    "Lower middle income",
    "Upper middle income",
    "High income",
]


class PredictionInput(BaseModel):
    """Entrada de /predict (contrato D2)."""

    energy_consumption: float = Field(..., gt=0, description="Consumo de energía (> 0).")
    renewable_energy: float = Field(
        ..., ge=0, description="Energía renovable (≥ 0 y ≤ energy_consumption)."
    )
    income_level: IncomeLevel = Field(..., description="Nivel de ingreso del World Bank.")

    @model_validator(mode="after")
    def renewable_not_above_consumption(self):
        if self.renewable_energy > self.energy_consumption:
            raise ValueError("renewable_energy no puede ser mayor que energy_consumption.")
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "energy_consumption": 500,
                    "renewable_energy": 120,
                    "income_level": "Upper middle income",
                }
            ]
        }
    }


class PredictionOutput(BaseModel):
    """Salida de /predict (contrato D2)."""

    segment_id: int
    segment_name: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput) -> PredictionOutput:
    # Base del paso 11.2: valida la entrada (422 si es inválida) pero todavía no
    # hay modelo. En el paso 17.1 se conecta con predict_segment() del MLE.
    raise HTTPException(status_code=503, detail="El modelo aún no está disponible.")
