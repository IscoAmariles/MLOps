"""Tests de src/predict.py (paso 14, MLE).

Los unitarios usan un modelo simulado (corren en el CI). El de integración
solo corre si hay un servidor de MLflow con el champion en 127.0.0.1:5000.
"""

import urllib.request

import pandas as pd
import pytest

from src import config, predict
from src.features import RAW_INPUT_COLUMNS


class FakeModel:
    def __init__(self, segment):
        self.segment = segment
        self.seen = None

    def predict(self, X):
        self.seen = X
        return [self.segment]


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeModel(segment=2)
    monkeypatch.setattr(predict, "load_model", lambda: model)
    return model


def test_predict_segment_devuelve_id_y_nombre(fake_model):
    out = predict.predict_segment(220, 200, "High income")
    assert out == {"segment_id": 2, "segment_name": config.SEGMENT_NAMES[2]}
    assert isinstance(out["segment_id"], int)


def test_predict_segment_envia_columnas_del_contrato(fake_model):
    predict.predict_segment(100, 10, "Low income")
    assert isinstance(fake_model.seen, pd.DataFrame)
    assert list(fake_model.seen.columns) == RAW_INPUT_COLUMNS
    assert fake_model.seen.iloc[0].tolist() == [100.0, 10.0, "Low income"]


def test_predict_segment_ingreso_desconocido(fake_model):
    with pytest.raises(ValueError, match="income_level"):
        predict.predict_segment(100, 10, "Rich")


def test_load_model_carga_una_sola_vez(monkeypatch):
    calls = []
    monkeypatch.setattr(predict.mlflow.sklearn, "load_model", lambda uri: calls.append(uri) or "m")
    predict.load_model.cache_clear()
    try:
        assert predict.load_model() == predict.load_model() == "m"
        assert calls == [config.MODEL_URI]
    finally:
        predict.load_model.cache_clear()


def _mlflow_up() -> bool:
    try:
        urllib.request.urlopen(f"{config.MLFLOW_TRACKING_URI}/health", timeout=1)
        return True
    except OSError:
        return False


@pytest.mark.skipif(not _mlflow_up(), reason="Servidor de MLflow no disponible")
@pytest.mark.parametrize(
    "consumption, renewable, income, expected",
    [
        (1200, 20, "High income", 0),            # EE. UU.
        (250, 35, "Upper middle income", 1),     # Colombia
        (220, 200, "High income", 2),            # Noruega
    ],
)
def test_champion_real_un_caso_por_segmento(consumption, renewable, income, expected):
    predict.load_model.cache_clear()
    out = predict.predict_segment(consumption, renewable, income)
    assert out["segment_id"] == expected
