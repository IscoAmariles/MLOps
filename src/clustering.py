"""Segmentos de países con KMeans (dueño: ML Engineer, paso 9).

Los segmentos son el target del modelo (decisión D1). ``Environmental_Status``
solo se usa para comparar los segmentos, nunca como entrada ni como target.

Ejecutar desde la raíz del repo para ver la selección de ``k`` y el reporte
de segmentos que se lleva al PO (paso 10)::

    python -m src.clustering
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline

from src import config
from src.features import make_preprocessor, renewable_share

# Variantes de variables probadas en la selección de k.
VARIANTS = {
    "log_con_ingreso": {"log_consumption": True, "use_income": True},
    "log_sin_ingreso": {"log_consumption": True, "use_income": False},
    "lineal_con_ingreso": {"log_consumption": False, "use_income": True},
    "lineal_sin_ingreso": {"log_consumption": False, "use_income": False},
}


def _kmeans_pipeline(k: int, variant: str) -> Pipeline:
    return Pipeline(
        [
            ("pre", make_preprocessor(**VARIANTS[variant])),
            ("kmeans", KMeans(n_clusters=k, n_init=10, random_state=config.RANDOM_STATE)),
        ]
    )


def evaluate_k(raw: pd.DataFrame, ks=range(2, 6), variants=None) -> pd.DataFrame:
    """Silhouette y tamaños para cada combinación variante × k."""
    rows = []
    for variant in variants or VARIANTS:
        for k in ks:
            pipe = _kmeans_pipeline(k, variant).fit(raw)
            labels = pipe["kmeans"].labels_
            Xt = pipe["pre"].transform(raw)
            sizes = sorted(np.bincount(labels, minlength=k).tolist(), reverse=True)
            rows.append(
                {
                    "variant": variant,
                    "k": k,
                    "silhouette": round(float(silhouette_score(Xt, labels)), 4),
                    "sizes": sizes,
                    "min_size": min(sizes),
                    "valid": min(sizes) >= config.MIN_SEGMENT_SIZE,
                }
            )
    return pd.DataFrame(rows)


def fit_segments(raw: pd.DataFrame, k: int | None = None, variant: str | None = None) -> np.ndarray:
    """Etiqueta cada país con su segmento.

    Los ids se renumeran por ``renewable_share`` medio ascendente (0 = el menos
    renovable), para que no cambien entre corridas y ``SEGMENT_NAMES`` siga valiendo.
    """
    k = k or config.CLUSTER_K
    variant = variant or config.CLUSTER_VARIANT
    labels = _kmeans_pipeline(k, variant).fit(raw)["kmeans"].labels_
    share = renewable_share(raw["energy_consumption"], raw["renewable_energy"])
    order = share.groupby(labels).mean().sort_values().index
    remap = {old: new for new, old in enumerate(order)}
    return np.array([remap[label] for label in labels])


def segment_report(gold: pd.DataFrame, labels) -> dict:
    """Material para nombrar los segmentos con el PO (paso 10)."""
    df = gold.assign(segment=labels)
    centroids = df.groupby("segment").agg(
        n=("Country", "size"),
        energy_consumption=("Energy_Consumption", "mean"),
        renewable_energy=("Renewable_Energy", "mean"),
        renewable_share=("Renewable_Share", "mean"),
        income_ordinal=(
            "Income_Level",
            lambda s: s.map(config.INCOME_LEVELS.index).mean(),
        ),
    ).round(3)
    countries = df.groupby("segment")["Country"].apply(list)
    crosstab = pd.crosstab(df["segment"], df["Environmental_Status"])
    return {"centroids": centroids, "countries": countries, "crosstab": crosstab}


def main() -> None:
    from src.data import load_data
    from src.features import gold_to_raw_inputs

    gold = load_data()
    raw = gold_to_raw_inputs(gold)

    results = evaluate_k(raw)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(config.REPORTS_DIR / "clustering_k_selection.csv", index=False)
    print("== Selección de k (válido = todos los segmentos >= "
          f"{config.MIN_SEGMENT_SIZE} países)")
    print(results.sort_values(["valid", "silhouette"], ascending=False).to_string(index=False))

    labels = fit_segments(raw)
    rep = segment_report(gold, labels)
    print(f"\n== Elegido: k={config.CLUSTER_K}, variante={config.CLUSTER_VARIANT}")
    print("\nCentroides (unidades originales):\n", rep["centroids"].to_string())
    print("\nPaíses por segmento:")
    for seg, countries in rep["countries"].items():
        name = config.SEGMENT_NAMES.get(seg, "?")
        print(f"  {seg} {name}: {', '.join(countries)}")
    print("\nSegmento × Environmental_Status:\n", rep["crosstab"].to_string())

    gold.assign(segment=labels)[
        ["Country", "Country_Code", "Income_Level", "Energy_Consumption",
         "Renewable_Energy", "Renewable_Share", "Environmental_Status", "segment"]
    ].to_csv(config.REPORTS_DIR / "segments.csv", index=False)


if __name__ == "__main__":
    main()
