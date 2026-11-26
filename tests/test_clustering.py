"""Tests de src/clustering.py (pasos 9 y 17.4, MLE)."""

import numpy as np
import pandas as pd
import pytest

from src import config
from src.clustering import VARIANTS, evaluate_k, fit_segments, segment_report
from src.data import load_data
from src.features import gold_to_raw_inputs


@pytest.fixture(scope="module")
def gold():
    return load_data()


@pytest.fixture(scope="module")
def raw(gold):
    return gold_to_raw_inputs(gold)


def test_variante_elegida_existe():
    assert config.CLUSTER_VARIANT in VARIANTS


def test_evaluate_k_cubre_variantes_y_k(raw):
    res = evaluate_k(raw, ks=[2, 3])
    assert set(res.columns) >= {"variant", "k", "silhouette", "sizes", "min_size", "valid"}
    assert len(res) == 2 * len(VARIANTS)
    assert res["silhouette"].between(-1, 1).all()


def test_todos_los_paises_tienen_segmento(raw):
    labels = fit_segments(raw)
    assert len(labels) == 20
    assert set(labels) == set(range(config.CLUSTER_K))


def test_clustering_reproducible(raw):
    np.testing.assert_array_equal(fit_segments(raw), fit_segments(raw))


def test_ids_ordenados_por_renewable_share(raw):
    # id 0 = menor share renovable medio; así los ids no cambian entre corridas.
    labels = fit_segments(raw)
    share = raw["renewable_energy"] / raw["energy_consumption"]
    means = share.groupby(labels).mean()
    assert list(means.index) == sorted(means.index)
    assert means.is_monotonic_increasing


def test_tamano_minimo_por_segmento(raw):
    sizes = pd.Series(fit_segments(raw)).value_counts()
    assert sizes.min() >= config.MIN_SEGMENT_SIZE


def test_cada_segmento_tiene_nombre_y_descripcion():
    assert sorted(config.SEGMENT_NAMES) == list(range(config.CLUSTER_K))
    assert sorted(config.SEGMENT_DESCRIPTIONS) == list(range(config.CLUSTER_K))


def test_segment_report(gold, raw):
    labels = fit_segments(raw)
    rep = segment_report(gold, labels)
    assert set(rep) == {"centroids", "countries", "crosstab"}
    # Centroides en unidades originales (no escaladas).
    assert rep["centroids"]["energy_consumption"].max() > 100
    assert rep["crosstab"].to_numpy().sum() == 20
