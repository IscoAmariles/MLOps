"""Tests de src/train.py (paso 12, MLE). Sin MLflow: solo la lógica de comparación."""

import pandas as pd
import pytest

from src.data import load_data
from src.features import RAW_INPUT_COLUMNS
from src.train import build_candidates, evaluate_models, prepare_training_data, select_best


@pytest.fixture(scope="module")
def training_data():
    return prepare_training_data(load_data())


def test_prepare_training_data(training_data):
    X, y = training_data
    assert list(X.columns) == RAW_INPUT_COLUMNS
    assert len(X) == len(y) == 20


def test_tres_candidatos_con_preprocesamiento():
    cands = build_candidates()
    assert list(cands) == ["logistic_regression", "random_forest", "gradient_boosting"]
    for pipe in cands.values():
        assert pipe.steps[0][0] == "pre"


def test_evaluate_models(training_data):
    X, y = training_data
    res = evaluate_models(build_candidates(), X, y)
    assert list(res["model"]) == ["logistic_regression", "random_forest", "gradient_boosting"]
    assert res["f1_macro_mean"].between(0, 1).all()
    assert (res["f1_macro_std"] >= 0).all()


def _res(rows):
    return pd.DataFrame(rows, columns=["model", "f1_macro_mean", "f1_macro_std"])


def test_desempate_mayor_f1():
    res = _res([("logistic_regression", 0.8, 0.0), ("random_forest", 0.9, 0.2),
                ("gradient_boosting", 0.85, 0.0)])
    assert select_best(res) == "random_forest"


def test_desempate_menor_desviacion():
    res = _res([("logistic_regression", 0.9, 0.1), ("random_forest", 0.9, 0.05),
                ("gradient_boosting", 0.9, 0.2)])
    assert select_best(res) == "random_forest"


def test_desempate_modelo_mas_simple():
    res = _res([("gradient_boosting", 1.0, 0.0), ("random_forest", 1.0, 0.0),
                ("logistic_regression", 1.0, 0.0)])
    assert select_best(res) == "logistic_regression"
