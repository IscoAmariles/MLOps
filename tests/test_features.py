"""Tests de src/features.py (paso 17.4, MLE)."""

import math

import numpy as np
import pandas as pd
import pytest

from src import config
from src.data import load_data
from src.features import (
    FEATURE_COLUMNS,
    RAW_INPUT_COLUMNS,
    build_features,
    encode_income,
    gold_to_raw_inputs,
    make_preprocessor,
    renewable_share,
)


# --- renewable_share ---------------------------------------------------------
def test_renewable_share_caso_conocido():
    assert renewable_share(200, 50) == pytest.approx(0.25)


def test_renewable_share_consumo_cero_es_indefinido():
    # Mismo criterio que el ETL: consumo 0 -> NaN.
    assert math.isnan(renewable_share(0, 0))


def test_renewable_share_vectorizado():
    out = renewable_share(pd.Series([100.0, 0.0]), pd.Series([30.0, 5.0]))
    assert out.iloc[0] == pytest.approx(0.3)
    assert np.isnan(out.iloc[1])


def test_renewable_share_coincide_con_el_gold():
    df = load_data()
    calc = renewable_share(df["Energy_Consumption"], df["Renewable_Energy"])
    np.testing.assert_allclose(calc, df["Renewable_Share"])


# --- encode_income -----------------------------------------------------------
@pytest.mark.parametrize(
    "level, expected",
    [
        ("Low income", 0),
        ("Lower middle income", 1),
        ("Upper middle income", 2),
        ("High income", 3),
    ],
)
def test_encode_income_ordinal(level, expected):
    assert encode_income(level) == expected


def test_encode_income_desconocido_lanza_error():
    with pytest.raises(ValueError, match="income_level"):
        encode_income("Very high income")


# --- gold_to_raw_inputs y build_features -------------------------------------
def test_gold_to_raw_inputs_usa_columnas_del_contrato():
    raw = gold_to_raw_inputs(load_data())
    assert list(raw.columns) == RAW_INPUT_COLUMNS
    assert len(raw) == 20


def test_build_features_columnas_y_valores():
    X = pd.DataFrame(
        {
            "energy_consumption": [100.0],
            "renewable_energy": [25.0],
            "income_level": ["High income"],
        }
    )
    out = build_features(X, log_consumption=False, use_income=True)
    assert list(out.columns) == FEATURE_COLUMNS
    assert out.loc[0, "energy_consumption"] == 100.0
    assert out.loc[0, "renewable_share"] == pytest.approx(0.25)
    assert out.loc[0, "income_ordinal"] == 3


def test_build_features_log_y_sin_ingreso():
    X = pd.DataFrame(
        {
            "energy_consumption": [99.0],
            "renewable_energy": [9.0],
            "income_level": ["Low income"],
        }
    )
    out = build_features(X, log_consumption=True, use_income=False)
    assert "income_ordinal" not in out.columns
    assert out.loc[0, "energy_consumption"] == pytest.approx(np.log1p(99.0))


# --- make_preprocessor -------------------------------------------------------
def test_preprocesador_estandariza():
    raw = gold_to_raw_inputs(load_data())
    Xt = make_preprocessor().fit_transform(raw)
    assert Xt.shape == (20, len(FEATURE_COLUMNS))
    np.testing.assert_allclose(Xt.mean(axis=0), 0, atol=1e-9)
    np.testing.assert_allclose(Xt.std(axis=0), 1, atol=1e-9)


def test_income_levels_vienen_de_config():
    # Un solo lugar define los niveles válidos (config.INCOME_LEVELS).
    for i, level in enumerate(config.INCOME_LEVELS):
        assert encode_income(level) == i
