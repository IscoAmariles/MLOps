"""Tests de la API (dueño: ML Engineer, paso 17.3).

Usan un ``predict_segment`` simulado: no necesitan MLflow ni Docker, así que
corren en el CI.

Los tests marcados ``xfail`` describen lo que falta del paso 17.1 del DE
(``/predict`` conectado al modelo y ``/metrics``). Cuando se haga merge de esa
parte pasan solos; ahí se quita el marcador (``strict`` evita olvidarlo).
"""

import pytest
from fastapi.testclient import TestClient

import api.main as api_main
from src import config

PENDIENTE_17_1 = pytest.mark.xfail(
    reason="Pendiente del paso 17.1 (DE): /predict con predict_segment y /metrics",
    strict=True,
)

VALID = {"energy_consumption": 220, "renewable_energy": 200, "income_level": "High income"}


def fake_predict_segment(energy_consumption, renewable_energy, income_level):
    return {"segment_id": 2, "segment_name": config.SEGMENT_NAMES[2]}


@pytest.fixture
def client(monkeypatch, tmp_path):
    # raising=False: hasta el paso 17.1 api.main todavía no importa predict_segment.
    monkeypatch.setattr(api_main, "predict_segment", fake_predict_segment, raising=False)
    # El log de predicciones va a una carpeta temporal, no a data/monitoring.
    monkeypatch.setattr(config, "PREDICTIONS_LOG_PATH", tmp_path / "log.csv")
    return TestClient(api_main.app)


# --- /health -----------------------------------------------------------------
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- /predict: entradas inválidas → 422 (contrato D2) ------------------------
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({**VALID, "energy_consumption": 0}, id="consumo-cero"),
        pytest.param({**VALID, "energy_consumption": -5}, id="consumo-negativo"),
        pytest.param({**VALID, "renewable_energy": -1}, id="renovable-negativa"),
        pytest.param({**VALID, "renewable_energy": 300}, id="renovable-mayor-que-consumo"),
        pytest.param({**VALID, "income_level": "Very high income"}, id="ingreso-inexistente"),
        pytest.param(
            {k: v for k, v in VALID.items() if k != "income_level"}, id="falta-un-campo"
        ),
        pytest.param({**VALID, "energy_consumption": "mucho"}, id="tipo-invalido"),
    ],
)
def test_predict_invalido_422(client, payload):
    assert client.post("/predict", json=payload).status_code == 422


# --- /predict válido y /metrics (paso 17.1) ----------------------------------
@PENDIENTE_17_1
def test_predict_valido(client):
    r = client.post("/predict", json=VALID)
    assert r.status_code == 200
    assert r.json() == {"segment_id": 2, "segment_name": config.SEGMENT_NAMES[2]}


@PENDIENTE_17_1
def test_predict_valido_escribe_log(client):
    client.post("/predict", json=VALID)
    client.post("/predict", json={**VALID, "energy_consumption": 0})  # inválido: no cuenta
    lines = config.PREDICTIONS_LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2  # encabezado + 1 predicción válida


@PENDIENTE_17_1
def test_metrics_cuenta_predicciones(client):
    client.post("/predict", json=VALID)
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "green_data_prediction_count_total" in r.text
    assert "green_data_segment_predictions_total" in r.text
    assert config.SEGMENT_NAMES[2] in r.text


def test_modelo_no_disponible_503(client, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("MLflow caído")

    monkeypatch.setattr(api_main, "predict_segment", broken, raising=False)
    r = client.post("/predict", json=VALID)
    assert r.status_code == 503
