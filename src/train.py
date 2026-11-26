"""Entrenamiento y registro del modelo (dueño: ML Engineer, pasos 12 y 13).

Con el servidor de MLflow encendido (paso 11.1), desde la raíz del repo::

    python -m src.train

Entrena Logistic Regression, Random Forest y Gradient Boosting (un run de
MLflow cada uno), elige el mejor por F1 macro y lo registra como
``green-data-segmentation`` con el alias ``champion``.
"""

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline

from src import config
from src.clustering import VARIANTS, evaluate_k, fit_segments
from src.data import load_data
from src.features import gold_to_raw_inputs, make_preprocessor

# Orden de simplicidad: es el último criterio de desempate.
SIMPLICITY_ORDER = ["logistic_regression", "random_forest", "gradient_boosting"]


def prepare_training_data(gold: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """X = columnas del contrato D2; y = segmento de KMeans (decisión D1)."""
    X = gold_to_raw_inputs(gold)
    y = pd.Series(fit_segments(X), name="segment")
    return X, y


def build_candidates() -> dict[str, Pipeline]:
    """Los 3 modelos del taller, cada uno con el mismo preprocesamiento."""
    rs = config.RANDOM_STATE
    estimators = {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=rs),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=rs),
        "gradient_boosting": GradientBoostingClassifier(random_state=rs),
    }
    return {
        name: Pipeline(
            [("pre", make_preprocessor(**VARIANTS[config.CLUSTER_VARIANT])), ("model", est)]
        )
        for name, est in estimators.items()
    }


def evaluate_models(candidates: dict[str, Pipeline], X, y) -> pd.DataFrame:
    """F1 macro con validación cruzada estratificada (20 filas: no hay test set)."""
    cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE)
    rows = []
    for name, pipe in candidates.items():
        scores = cross_validate(pipe, X, y, cv=cv, scoring="f1_macro")["test_score"]
        rows.append(
            {
                "model": name,
                "f1_macro_mean": float(scores.mean()),
                "f1_macro_std": float(scores.std()),
                "f1_macro_folds": [round(float(s), 4) for s in scores],
            }
        )
    return pd.DataFrame(rows)


def select_best(results: pd.DataFrame) -> str:
    """Desempate fijado antes de entrenar: mayor F1, menor desviación, más simple."""
    ranked = results.assign(
        _simplicity=results["model"].map(SIMPLICITY_ORDER.index)
    ).sort_values(
        ["f1_macro_mean", "f1_macro_std", "_simplicity"], ascending=[False, True, True]
    )
    return ranked.iloc[0]["model"]


def main() -> None:
    gold = load_data()
    X, y = prepare_training_data(gold)

    k_selection = evaluate_k(X)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    k_path = config.REPORTS_DIR / "clustering_k_selection.csv"
    k_selection.to_csv(k_path, index=False)
    chosen = k_selection.query(
        "variant == @config.CLUSTER_VARIANT and k == @config.CLUSTER_K"
    ).iloc[0]

    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.EXPERIMENT_NAME)

    candidates = build_candidates()
    results = evaluate_models(candidates, X, y)
    results.to_csv(config.REPORTS_DIR / "model_comparison.csv", index=False)
    best = select_best(results)

    signature = infer_signature(X, y)
    for row in results.itertuples():
        with mlflow.start_run(run_name=row.model):
            pipe = candidates[row.model]
            mlflow.log_params({f"model__{k}": v for k, v in pipe["model"].get_params().items()})
            mlflow.log_params(
                {
                    "cluster_k": config.CLUSTER_K,
                    "cluster_variant": config.CLUSTER_VARIANT,
                    "cv_folds": config.CV_FOLDS,
                    "random_state": config.RANDOM_STATE,
                    "n_rows": len(X),
                }
            )
            mlflow.log_metrics(
                {
                    "f1_macro_mean": row.f1_macro_mean,
                    "f1_macro_std": row.f1_macro_std,
                    "cluster_silhouette": float(chosen["silhouette"]),
                }
            )
            mlflow.set_tag("champion_candidate", str(row.model == best).lower())
            mlflow.log_artifact(str(k_path))

            if row.model == best:
                # Sin datos de sobra: el elegido se reentrena con los 20 países.
                pipe.fit(X, y)
                info = mlflow.sklearn.log_model(
                    pipe,
                    name="model",
                    signature=signature,
                    input_example=X.head(3),
                    code_paths=["src"],
                    # MLflow 3 serializa con skops: nuestra función de features
                    # es código propio del repo, así que se declara confiable.
                    skops_trusted_types=["src.features.build_features"],
                    registered_model_name=config.MODEL_NAME,
                )
                version = info.registered_model_version
                MlflowClient().set_registered_model_alias(
                    config.MODEL_NAME, config.MODEL_ALIAS, version
                )

    print(results.drop(columns="f1_macro_folds").to_string(index=False))
    print(f"\nChampion: {best} -> {config.MODEL_URI} (versión {version})")


if __name__ == "__main__":
    main()
