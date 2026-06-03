"""
Gera dataset tabular para treino do modelo yield_risk (local, sem GCP).

Uso:
  python scripts/generate_training_dataset.py
  python scripts/generate_training_dataset.py --rows 10000 --out data/training/yield_risk_v1.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core_logic.orchestrator import compute_yield_risk_score
from src.ml_models.ndvi_processor import simulate_sentinel_bands, process_field


def generate_row(rng: np.random.Generator) -> dict:
    stress_fraction = float(rng.uniform(0.08, 0.42))
    seed = int(rng.integers(0, 1_000_000))
    soil = float(rng.uniform(10.0, 45.0))

    red, nir = simulate_sentinel_bands(
        height=128,
        width=128,
        stress_fraction=stress_fraction,
        seed=seed,
    )
    result = process_field(red, nir)
    summary = result.summary

    ndvi_hint = int(summary["yield_risk_hint"])
    label = compute_yield_risk_score(ndvi_hint, soil)

    return {
        "ndvi_mean": summary["ndvi_mean"],
        "ndvi_std": summary["ndvi_std"],
        "stress_pct_severe": summary["stress_pct_severe"],
        "stress_pct_attention": summary["stress_pct_attention"],
        "stress_pct_healthy": summary["stress_pct_healthy"],
        "soil_moisture_pct": round(soil, 2),
        "stress_fraction": round(stress_fraction, 4),
        "yield_risk_score": label,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera dataset yield_risk OrbitalBasis")
    parser.add_argument("--rows", type=int, default=8000, help="Número de amostras")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "training" / "yield_risk_v1.parquet",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    rows = [generate_row(rng) for _ in range(args.rows)]
    df = pd.DataFrame(rows)
    df.to_parquet(args.out, index=False)

    print(f"Dataset salvo: {args.out}")
    print(f"Linhas: {len(df)}")
    print(f"yield_risk_score — min={df['yield_risk_score'].min()} max={df['yield_risk_score'].max()} mean={df['yield_risk_score'].mean():.1f}")


if __name__ == "__main__":
    main()
