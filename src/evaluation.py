import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - predicted)))


def rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def r2(actual: np.ndarray, predicted: np.ndarray) -> float:
    ss_res = float(np.sum((actual - predicted) ** 2))
    ss_tot = float(np.sum((actual - np.mean(actual)) ** 2))

    return float(1 - ss_res / ss_tot) if ss_tot else 0.0


def create_model_comparison_chart(output_dir: Path) -> None:
    ceren_metrics_path = output_dir / "ceren_linear_regression_metrics.json"
    taha_metrics_path = output_dir / "taha_random_forest_metrics.json"

    if not ceren_metrics_path.exists() or not taha_metrics_path.exists():
        print("\n[Model Comparison] Metrics files not found. Skipping comparison chart.")
        return

    ceren_metrics = json.loads(
        ceren_metrics_path.read_text(encoding="utf-8")
    )

    taha_metrics = json.loads(
        taha_metrics_path.read_text(encoding="utf-8")
    )

    comparison_df = pd.DataFrame(
        [
            {
                "model": "Linear Regression",
                "mae": ceren_metrics["metrics"]["mae"],
                "rmse": ceren_metrics["metrics"]["rmse"],
                "r2": ceren_metrics["metrics"]["r2"],
            },
            {
                "model": "Random Forest",
                "mae": taha_metrics["metrics"]["mae"],
                "rmse": taha_metrics["metrics"]["rmse"],
                "r2": taha_metrics["metrics"]["r2"],
            },
        ]
    )

    comparison_df.to_csv(
        output_dir / "model_comparison_metrics.csv",
        index=False,
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(comparison_df["model"], comparison_df["mae"])
    ax.set_title("Model Comparison by MAE", fontweight="bold")
    ax.set_ylabel("MAE Lower is Better")
    ax.grid(True, alpha=0.3, axis="y")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(output_dir / "model_comparison_mae.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(comparison_df["model"], comparison_df["rmse"])
    ax.set_title("Model Comparison by RMSE", fontweight="bold")
    ax.set_ylabel("RMSE Lower is Better")
    ax.grid(True, alpha=0.3, axis="y")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(output_dir / "model_comparison_rmse.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(comparison_df["model"], comparison_df["r2"])
    ax.set_title("Model Comparison by R2", fontweight="bold")
    ax.set_ylabel("R2 Higher is Better")
    ax.grid(True, alpha=0.3, axis="y")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(output_dir / "model_comparison_r2.png", dpi=150)
    plt.close(fig)

    print("\n=== MODEL COMPARISON ===")
    print(comparison_df.to_string(index=False))
    print(f"Model comparison CSV saved → {output_dir / 'model_comparison_metrics.csv'}")
    print(f"MAE chart saved → {output_dir / 'model_comparison_mae.png'}")
    print(f"RMSE chart saved → {output_dir / 'model_comparison_rmse.png'}")
    print(f"R2 chart saved → {output_dir / 'model_comparison_r2.png'}")