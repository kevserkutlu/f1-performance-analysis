import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

from evaluation import mae, rmse, r2


def random_forest(
    frame: pd.DataFrame,
    output_dir: Path,
) -> dict:
    target = "finish_position"

    frame = frame.copy()

    # Taha's Feature 1: recent improvement trend
    frame["driver_recent_improvement"] = (
    frame["last_5_race_avg_finish"] - frame["last_3_race_avg_finish"]
)

    # Taha's Feature 2: driver consistency
    frame["driver_consistency_score"] = (
        frame["last_3_race_avg_finish"]
        - frame["last_5_race_avg_finish"]
    ).abs()

    feature_columns = [
        "grid",
        "driver_form_score",
        "weekend_readiness",
        "driver_season_momentum",
        "driver_recent_improvement",
        "driver_consistency_score",
    ]

    model_df = frame[
        feature_columns
        + [
            target,
            "season",
        ]
    ].copy()

    for col in feature_columns + [target]:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.dropna()

    train_df = model_df[model_df["season"] <= 2023].copy()
    test_df = model_df[model_df["season"] == 2024].copy()

    x_train = train_df[feature_columns]
    y_train = train_df[target]

    x_test = test_df[feature_columns]
    y_test = test_df[target].to_numpy(float)

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=8,
    )

    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    predictions = np.clip(predictions, 1, 20)

    # ─────────────────────────────────────────────
    # Metrics
    # ─────────────────────────────────────────────

    metrics = {
        "model": "Random Forest Regressor",
        "owner": "Taha",
        "train_seasons": "2018-2023",
        "test_season": 2024,
        "target": target,
        "features_used_in_model": feature_columns,
        "engineered_features": {
           "driver_recent_improvement": "last_5_race_avg_finish - last_3_race_avg_finish",
            "driver_consistency_score": "absolute difference between last 3 race average finish and last 5 race average finish",
        },
        "analysis_notes": {
            "model_type": "Non-linear ensemble model",
            "reason_for_selection": "Random Forest was selected because race performance depends on non-linear interactions between grid position, recent form, season momentum and driver consistency.",
            "interpretability": "Feature importance was used to explain which variables contributed most to the model predictions.",
        },
        "metrics": {
            "mae": mae(y_test, predictions),
            "rmse": rmse(y_test, predictions),
            "r2": r2(y_test, predictions),
        },
    }

    (output_dir / "taha_random_forest_metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print("\n=== TAHA'S RANDOM FOREST ===")
    print(json.dumps(metrics["metrics"], indent=2))

    # ─────────────────────────────────────────────
    # Prediction CSV
    # ─────────────────────────────────────────────

    result_df = test_df.copy()

    result_df["taha_predicted_finish_position"] = np.round(predictions, 2)

    result_df["absolute_error"] = np.round(
        np.abs(
            result_df[target]
            - result_df["taha_predicted_finish_position"]
        ),
        2,
    )

    result_df.to_csv(
        output_dir / "taha_random_forest_predictions_2024.csv",
        index=False,
    )

    print(
        f"Predictions saved → "
        f"{output_dir / 'taha_random_forest_predictions_2024.csv'}"
    )

    # ─────────────────────────────────────────────
    # Top prediction errors CSV
    # ─────────────────────────────────────────────

    top_errors = result_df.sort_values(
        "absolute_error",
        ascending=False,
    ).head(10)

    top_errors.to_csv(
        output_dir / "taha_random_forest_top_prediction_errors.csv",
        index=False,
    )

    print(
        f"Top prediction errors saved → "
        f"{output_dir / 'taha_random_forest_top_prediction_errors.csv'}"
    )

    # ─────────────────────────────────────────────
    # Feature importance graph
    # ─────────────────────────────────────────────

    importance_df = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=True)

    importance_df.to_csv(
        output_dir / "taha_random_forest_feature_importance.csv",
        index=False,
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(
        importance_df["feature"],
        importance_df["importance"],
        color="#E10600",
    )

    ax.set_xlabel("Feature Importance")
    ax.set_title("Taha's Random Forest Feature Importance", fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    sns.despine(ax=ax)

    fig.tight_layout()

    fig.savefig(
        output_dir / "taha_random_forest_feature_importance.png",
        dpi=150,
    )

    plt.close(fig)

    print(
        f"Feature importance chart saved → "
        f"{output_dir / 'taha_random_forest_feature_importance.png'}"
    )

    # ─────────────────────────────────────────────
    # Actual vs Predicted graph
    # ─────────────────────────────────────────────

    fig, ax = plt.subplots(figsize=(7, 7))

    ax.scatter(
        y_test,
        predictions,
        alpha=0.45,
        color="#E10600",
        s=25,
    )

    ax.plot(
        [1, 20],
        [1, 20],
        linestyle="--",
        linewidth=1,
        color="black",
        label="Perfect prediction",
    )

    ax.set_xlabel("Actual Finish Position")
    ax.set_ylabel("Predicted Finish Position")
    ax.set_title(
        "Taha's Random Forest: Actual vs Predicted",
        fontweight="bold",
    )

    ax.set_xlim(1, 20)
    ax.set_ylim(1, 20)
    ax.grid(True, alpha=0.3)
    ax.legend()

    sns.despine(ax=ax)

    fig.tight_layout()

    fig.savefig(
        output_dir / "taha_random_forest_actual_vs_predicted.png",
        dpi=150,
    )

    plt.close(fig)

    print(
        f"Actual vs predicted chart saved → "
        f"{output_dir / 'taha_random_forest_actual_vs_predicted.png'}"
    )

    # ─────────────────────────────────────────────
    # Error distribution graph
    # ─────────────────────────────────────────────

    errors = y_test - predictions

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(
        errors,
        bins=20,
        color="#E10600",
        alpha=0.75,
    )

    ax.axvline(
        0,
        color="black",
        linestyle="--",
        linewidth=1,
    )

    ax.set_title(
        "Taha's Random Forest Prediction Error Distribution",
        fontweight="bold",
    )

    ax.set_xlabel("Prediction Error (Actual Finish Position - Predicted Finish Position)")
    ax.set_ylabel("Frequency")

    ax.text(
        0.98,
        0.95,
        "Negative values indicate overestimation.\nPositive values indicate underestimation.",
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
    )

    ax.grid(True, alpha=0.3)

    sns.despine(ax=ax)

    fig.tight_layout()

    fig.savefig(
        output_dir / "taha_random_forest_error_distribution.png",
        dpi=150,
    )

    plt.close(fig)

    print(
        f"Error distribution chart saved → "
        f"{output_dir / 'taha_random_forest_error_distribution.png'}"
    )

    # ─────────────────────────────────────────────
    # Top features printed
    # ─────────────────────────────────────────────

    top_features = importance_df.sort_values(
        "importance",
        ascending=False,
    ).head(3)

    print("\n===Taha'S TOP 3 RANDOM FOREST FEATURES ===")
    print(top_features.to_string(index=False))

    return metrics