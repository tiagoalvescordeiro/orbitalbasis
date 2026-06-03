"""
Treina Random Forest para yield_risk_score (local, sem Vertex AI).

Uso:
  python scripts/generate_training_dataset.py
  python scripts/train_yield_risk.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ml_models.yield_risk_predictor import DEFAULT_METRICS_PATH, DEFAULT_MODEL_PATH, FEATURE_COLUMNS

try:
    import joblib
except ImportError:
    joblib = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Treina modelo yield_risk OrbitalBasis")
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "training" / "yield_risk_v1.parquet",
    )
    parser.add_argument(
        "--model-out",
        type=Path,
        default=DEFAULT_MODEL_PATH,
    )
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=DEFAULT_METRICS_PATH,
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not args.data.exists():
        print(f"Dataset não encontrado: {args.data}")
        print("Execute: python scripts/generate_training_dataset.py")
        sys.exit(1)

    if joblib is None:
        print("joblib não disponível (instale scikit-learn).")
        sys.exit(1)

    df = pd.read_parquet(args.data)
    missing = [c for c in FEATURE_COLUMNS + ["yield_risk_score"] if c not in df.columns]
    if missing:
        print(f"Colunas ausentes no dataset: {missing}")
        sys.exit(1)

    x = df[FEATURE_COLUMNS].values
    y = df["yield_risk_score"].values.astype(np.float64)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=args.test_size, random_state=args.seed
    )

    model = RandomForestRegressor(
        n_estimators=120,
        max_depth=12,
        min_samples_leaf=4,
        random_state=args.seed,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    pred_test = model.predict(x_test)
    mae = float(mean_absolute_error(y_test, pred_test))
    r2 = float(r2_score(y_test, pred_test))

    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, args.model_out)

    metrics = {
        "model": "RandomForestRegressor",
        "n_estimators": 120,
        "rows_total": int(len(df)),
        "rows_train": int(len(x_train)),
        "rows_test": int(len(x_test)),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "features": FEATURE_COLUMNS,
        "target": "yield_risk_score",
        "note": "Label = heurística OrbitalBasis (NDVI + solo). POC FIAP — substituir por dados reais depois.",
    }
    args.metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Modelo salvo: {args.model_out}")
    print(f"Métricas: {args.metrics_out}")
    print(f"MAE={mae:.2f}  R²={r2:.4f}")


if __name__ == "__main__":
    main()
