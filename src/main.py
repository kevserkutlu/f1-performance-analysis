"""
F1 Race Prediction Pipeline
- Ceren's Linear Regression model (adapted from ceren_linear_regression.py)
- 3 data insights: grid effect, pit stop strategy, constructor reliability
- 1 new engineered feature: driver_season_momentum
- 1 EDA chart: average finish position by starting grid position
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "f1_2018_2024_wow_master_dataset.csv"
OUTPUT_DIR = BASE_DIR / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# NEW FEATURE
# ─────────────────────────────────────────────────────────────────────────────

def add_new_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add driver_season_momentum: average championship points earned per race
    so far in the current season before this event.

    Motivation: raw season points favour late-season races; dividing by races
    run gives a rate that is comparable across the calendar.
    """
    df = df.copy()
    df["driver_season_momentum"] = df["driver_season_points_before_race"] / df[
        "driver_season_races_before_race"
    ].replace(0, np.nan)
    df["driver_season_momentum"] = df["driver_season_momentum"].fillna(0.0)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# DATA INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────

def insight_grid_effect(df: pd.DataFrame) -> None:
    """Insight 1 – Grid position vs. finish position.

    Starting from pole rarely guarantees a win, but front-row starters
    finish on average far ahead of the midfield.
    """
    finished = df[(df["finished_flag"] == 1) & (df["grid"] > 0)]
    corr = finished["grid"].corr(finished["finish_position"])

    avg_finish_by_grid = (
        finished.groupby("grid")["finish_position"]
        .mean()
        .reset_index()
        .rename(columns={"finish_position": "avg_finish"})
    )
    top5_grid_avg = avg_finish_by_grid[avg_finish_by_grid["grid"] <= 5]["avg_finish"].mean()
    mid_grid_avg = avg_finish_by_grid[
        (avg_finish_by_grid["grid"] >= 6) & (avg_finish_by_grid["grid"] <= 10)
    ]["avg_finish"].mean()

    print("\n=== INSIGHT 1: Grid Position Effect ===")
    print(f"  Pearson correlation (grid vs finish): {corr:.3f}")
    print(f"  Avg finish for P1-P5 starters:        {top5_grid_avg:.2f}")
    print(f"  Avg finish for P6-P10 starters:       {mid_grid_avg:.2f}")
    print(f"  Front-row starters finish ~{mid_grid_avg - top5_grid_avg:.1f} places better on average.")


def insight_pit_stop_strategy(df: pd.DataFrame) -> None:
    """Insight 2 – Pit stop count vs. finish position.

    In modern F1 (2018-2024) a one-stop strategy is standard; drivers who
    pit twice or more tend to start further back or face tyre problems.
    """
    finished = df[
        (df["finished_flag"] == 1) & (df["pit_stop_count"] > 0) & (df["pit_stop_count"] <= 4)
    ]
    summary = (
        finished.groupby("pit_stop_count")["finish_position"]
        .agg(avg="mean", count="size")
        .reset_index()
    )
    print("\n=== INSIGHT 2: Pit Stop Strategy ===")
    print(summary.to_string(index=False))
    one_stop = summary.loc[summary["pit_stop_count"] == 1, "avg"].values
    two_stop = summary.loc[summary["pit_stop_count"] == 2, "avg"].values
    if one_stop.size and two_stop.size:
        delta = two_stop[0] - one_stop[0]
        print(f"  2-stop vs 1-stop avg finish gap: {delta:+.2f} positions")


def insight_constructor_reliability(df: pd.DataFrame) -> None:
    """Insight 3 – DNF rate by constructor.

    Reliability is a decisive championship factor; top constructors
    consistently keep both cars running to the flag.
    """
    constructors = df.groupby("constructor_name").agg(
        total_starts=("dnf_flag", "size"),
        total_dnfs=("dnf_flag", "sum"),
    )
    constructors["dnf_rate_pct"] = (constructors["total_dnfs"] / constructors["total_starts"] * 100).round(1)
    constructors = constructors[constructors["total_starts"] >= 30].sort_values("dnf_rate_pct")

    print("\n=== INSIGHT 3: Constructor DNF Rates (min 30 starts) ===")
    print(constructors[["total_starts", "total_dnfs", "dnf_rate_pct"]].to_string())


# ─────────────────────────────────────────────────────────────────────────────
# EDA CHART
# ─────────────────────────────────────────────────────────────────────────────

def plot_grid_vs_finish(df: pd.DataFrame, output_path: Path) -> None:
    """EDA chart: average finish position by starting grid slot (P1–P20).

    Shows the monotonic advantage of qualifying higher alongside variance
    (IQR band) to illustrate that mid-grid is the most unpredictable zone.
    """
    finished = df[(df["finished_flag"] == 1) & (df["grid"].between(1, 20))]
    stats = finished.groupby("grid")["finish_position"].agg(["mean", "median", "std"]).reset_index()
    stats.columns = ["grid", "mean", "median", "std"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.fill_between(
        stats["grid"],
        (stats["mean"] - stats["std"]).clip(lower=1),
        (stats["mean"] + stats["std"]).clip(upper=20),
        alpha=0.2,
        color="#E10600",
        label="±1 std dev",
    )
    ax.plot(stats["grid"], stats["mean"], color="#E10600", linewidth=2.5, marker="o", label="Mean finish")
    ax.plot(stats["grid"], stats["median"], color="#1f77b4", linewidth=1.5, linestyle="--", marker="s", label="Median finish")
    ax.plot(stats["grid"], stats["grid"], color="gray", linewidth=1, linestyle=":", label="Grid = Finish (no change)")

    ax.set_xlabel("Starting Grid Position", fontsize=13)
    ax.set_ylabel("Finish Position", fontsize=13)
    ax.set_title("Average Finish Position by Starting Grid (2018–2024)", fontsize=15, fontweight="bold")
    ax.set_xticks(range(1, 21))
    ax.set_yticks(range(1, 21))
    ax.invert_yaxis()
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    sns.despine(ax=ax)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"\n  EDA chart saved → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# CEREN'S LINEAR REGRESSION
# ─────────────────────────────────────────────────────────────────────────────

def mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - predicted)))


def rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def r2(actual: np.ndarray, predicted: np.ndarray) -> float:
    ss_res = float(np.sum((actual - predicted) ** 2))
    ss_tot = float(np.sum((actual - np.mean(actual)) ** 2))
    return float(1 - ss_res / ss_tot) if ss_tot else 0.0


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame = frame[(frame["finish_position"].notna()) & (frame["grid"] > 0)].copy()
    frame["qualifying_position"] = frame["qualifying_position"].fillna(frame["grid"])

    frame["driver_form_score"] = (
        0.7 * frame["last_3_race_avg_finish"] + 0.3 * frame["last_5_race_avg_finish"]
    )
    frame["weekend_readiness"] = (
        0.5 * frame["qualifying_position"]
        + 0.3 * frame["driver_prev_circuit_avg_finish"]
        + 0.2 * frame["driver_championship_position_before_race"]
    )
    return frame


def fit_linear_regression(
    train_df: pd.DataFrame, test_df: pd.DataFrame, features: list[str], target: str
) -> tuple[np.ndarray, np.ndarray]:
    x_train = train_df[features].to_numpy(float)
    x_test = test_df[features].to_numpy(float)
    y_train = train_df[target].to_numpy(float)

    x_train = np.column_stack([np.ones(len(x_train)), x_train])
    x_test = np.column_stack([np.ones(len(x_test)), x_test])

    beta, *_ = np.linalg.lstsq(x_train, y_train, rcond=None)
    predictions = x_test @ beta
    return beta, predictions


# ─────────────────────────────────────────────────────────────────────────────
# KEVSER'S MODEL DIAGNOSTICS
# ─────────────────────────────────────────────────────────────────────────────

def plot_model_diagnostics(
    actual: np.ndarray,
    predicted: np.ndarray,
    beta: np.ndarray,
    features: list[str],
    output_path: Path,
) -> None:
    residuals = actual - predicted

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1 – Actual vs. Predicted
    ax = axes[0]
    ax.scatter(actual, predicted, alpha=0.35, color="#E10600", s=18)
    lims = [1, 20]
    ax.plot(lims, lims, "k--", linewidth=1, label="Perfect prediction")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Actual Finish Position", fontsize=12)
    ax.set_ylabel("Predicted Finish Position", fontsize=12)
    ax.set_title("Actual vs. Predicted", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    sns.despine(ax=ax)

    # 2 – Feature Coefficients (excluding intercept)
    ax = axes[1]
    coef_names = features
    coef_vals = beta[1:]
    colors = ["#E10600" if v > 0 else "#1f77b4" for v in coef_vals]
    bars = ax.barh(coef_names, coef_vals, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    for bar, val in zip(bars, coef_vals):
        ax.text(
            val + (0.01 if val >= 0 else -0.01),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}",
            va="center",
            ha="left" if val >= 0 else "right",
            fontsize=9,
        )
    ax.set_xlabel("Coefficient Value", fontsize=12)
    ax.set_title("Feature Coefficients", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")
    sns.despine(ax=ax)

    # 3 – Residuals vs. Predicted
    ax = axes[2]
    ax.scatter(predicted, residuals, alpha=0.35, color="#1f77b4", s=18)
    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.set_xlabel("Predicted Finish Position", fontsize=12)
    ax.set_ylabel("Residual (Actual − Predicted)", fontsize=12)
    ax.set_title("Residuals vs. Predicted", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3)
    sns.despine(ax=ax)

    fig.suptitle(
        "Kevser's Model Diagnostics – Ceren's Linear Regression (2024 Test Set)",
        fontsize=14, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"  Diagnostics chart saved → {output_path}")


def run_ceren_linear_regression(frame: pd.DataFrame) -> None:
    target = "finish_position"
    feature_columns = [
        "grid",
        "driver_form_score",
        "weekend_readiness",
        "driver_season_momentum",
    ]

    train_df = frame[frame["season"] <= 2023].copy()
    test_df = frame[frame["season"] == 2024].copy()

    if test_df.empty:
        print("\n  [Ceren LR] No 2024 data found for testing — skipping.")
        return

    beta, predictions = fit_linear_regression(train_df, test_df, feature_columns, target)
    predictions = np.clip(predictions, 1, 20)
    actual = test_df[target].to_numpy(float)

    metrics = {
        "train_seasons": "2018-2023",
        "test_season": 2024,
        "rows_train": int(len(train_df)),
        "rows_test": int(len(test_df)),
        "target": target,
        "features_used_in_model": feature_columns,
        "engineered_features": {
            "driver_form_score": "0.7 * last_3_race_avg_finish + 0.3 * last_5_race_avg_finish",
            "weekend_readiness": "0.5 * qualifying_position + 0.3 * driver_prev_circuit_avg_finish + 0.2 * driver_championship_position_before_race",
            "driver_season_momentum": "driver_season_points_before_race / driver_season_races_before_race",
        },
        "coefficients": {
            "intercept": float(beta[0]),
            "grid": float(beta[1]),
            "driver_form_score": float(beta[2]),
            "weekend_readiness": float(beta[3]),
            "driver_season_momentum": float(beta[4]),
        },
        "metrics": {
            "mae": mae(actual, predictions),
            "rmse": rmse(actual, predictions),
            "r2": r2(actual, predictions),
        },
    }

    result_df = test_df[
        [
            "season", "race_round", "race_name", "driver_full_name", "constructor_name",
            "grid", "qualifying_position", "driver_form_score", "weekend_readiness",
            "driver_season_momentum", "finish_position",
        ]
    ].copy()
    result_df["predicted_finish_position"] = np.round(predictions, 2)
    result_df["absolute_error"] = np.round(
        np.abs(result_df["finish_position"] - result_df["predicted_finish_position"]), 2
    )

    result_df.to_csv(OUTPUT_DIR / "ceren_linear_regression_predictions_2024.csv", index=False)
    (OUTPUT_DIR / "ceren_linear_regression_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    print("\n=== CEREN'S LINEAR REGRESSION ===")
    print(json.dumps(metrics["metrics"], indent=2))
    print(f"  Predictions saved → {OUTPUT_DIR / 'ceren_linear_regression_predictions_2024.csv'}")

    plot_model_diagnostics(
        actual, predictions, beta, feature_columns,
        OUTPUT_DIR / "ceren_lr_diagnostics.png",
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Loading data from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"  Shape: {df.shape}  |  Seasons: {sorted(df['season'].unique())}")

    # ── New feature ──────────────────────────────────────────────────────────
    df = add_new_features(df)
    print("\n[+] New feature added: 'driver_season_momentum'")
    print(f"    = driver_season_points_before_race / driver_season_races_before_race")
    print(f"    Sample stats:\n{df['driver_season_momentum'].describe().round(2)}")

    # ── Three insights ───────────────────────────────────────────────────────
    insight_grid_effect(df)
    insight_pit_stop_strategy(df)
    insight_constructor_reliability(df)

    # ── EDA chart ────────────────────────────────────────────────────────────
    plot_grid_vs_finish(df, OUTPUT_DIR / "eda_grid_vs_finish.png")

    # ── Ceren's model + Kevser's diagnostics ─────────────────────────────────
    frame = build_features(df)
    run_ceren_linear_regression(frame)


if __name__ == "__main__":
    main()
