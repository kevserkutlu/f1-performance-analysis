from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.ensemble import RandomForestRegressor


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "f1_2018_2024_wow_master_dataset.csv"

FEATURE_COLUMNS = [
    "grid",
    "driver_form_score",
    "weekend_readiness",
    "driver_season_momentum",
    "driver_recent_improvement",
    "driver_consistency_score",
]


def _compute_engineered_features(payload: Dict[str, Any]) -> Dict[str, float]:
    # driver_form_score
    if "driver_form_score" in payload:
        driver_form_score = float(payload["driver_form_score"])
    else:
        last3 = float(payload.get("last_3_race_avg_finish", 0.0))
        last5 = float(payload.get("last_5_race_avg_finish", 0.0))
        driver_form_score = 0.7 * last3 + 0.3 * last5

    # weekend_readiness
    if "weekend_readiness" in payload:
        weekend_readiness = float(payload["weekend_readiness"])
    else:
        qualifying = float(payload.get("qualifying_position", payload.get("grid", 0)))
        prev_circuit = float(payload.get("driver_prev_circuit_avg_finish", 0.0))
        champ_pos = float(payload.get("driver_championship_position_before_race", 0.0))
        weekend_readiness = 0.5 * qualifying + 0.3 * prev_circuit + 0.2 * champ_pos

    # driver_season_momentum
    if "driver_season_momentum" in payload:
        driver_season_momentum = float(payload["driver_season_momentum"])
    else:
        pts = float(payload.get("driver_season_points_before_race", 0.0))
        races = float(payload.get("driver_season_races_before_race", 0.0))
        driver_season_momentum = pts / races if races else 0.0

    # recent improvement and consistency
    last3 = float(payload.get("last_3_race_avg_finish", 0.0))
    last5 = float(payload.get("last_5_race_avg_finish", 0.0))
    driver_recent_improvement = last5 - last3
    driver_consistency_score = abs(last3 - last5)

    return {
        "driver_form_score": driver_form_score,
        "weekend_readiness": weekend_readiness,
        "driver_season_momentum": driver_season_momentum,
        "driver_recent_improvement": driver_recent_improvement,
        "driver_consistency_score": driver_consistency_score,
    }


def _train_model() -> RandomForestRegressor:
    df = pd.read_csv(DATA_PATH)

    try:
        from main import add_new_features, build_features

        df = add_new_features(df)
        df = build_features(df)
    except Exception:
        df["driver_season_momentum"] = df["driver_season_points_before_race"].fillna(0) / df[
            "driver_season_races_before_race"
        ].replace(0, np.nan).fillna(0)
        df["driver_form_score"] = (
            0.7 * df.get("last_3_race_avg_finish", 0)
            + 0.3 * df.get("last_5_race_avg_finish", 0)
        )
        df["weekend_readiness"] = (
            0.5 * df.get("qualifying_position", df.get("grid", 0))
            + 0.3 * df.get("driver_prev_circuit_avg_finish", 0)
            + 0.2 * df.get("driver_championship_position_before_race", 0)
        )

    df["driver_recent_improvement"] = df["last_5_race_avg_finish"] - df["last_3_race_avg_finish"]
    df["driver_consistency_score"] = (
        df["last_3_race_avg_finish"] - df["last_5_race_avg_finish"]
    ).abs()

    model_df = df[FEATURE_COLUMNS + ["finish_position", "season"]].copy()
    for col in FEATURE_COLUMNS + ["finish_position"]:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.dropna()

    train_df = model_df[model_df["season"] <= 2023]
    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["finish_position"]

    model = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=8)
    model.fit(x_train, y_train)
    return model


MODEL = _train_model()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)  # Esra'nın frontend'inin erişebilmesi için

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "status": "ok",
            "message": "F1 Performance Prediction API 🏎️",
            "endpoints": {
                "GET  /": "Bu mesaj",
                "GET  /health": "Sağlık kontrolü",
                "POST /predict": "Yarış bitiş pozisyonu tahmini",
            },
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "model": "RandomForestRegressor",
            "features": FEATURE_COLUMNS,
        })

    @app.route("/predict", methods=["POST"])
    def predict():
        payload = request.get_json(force=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "JSON body required"}), 400

        if "grid" not in payload:
            return jsonify({"error": "'grid' field is required"}), 400

        grid = float(payload["grid"])
        engineered = _compute_engineered_features(payload)

        row = [
            grid,
            engineered["driver_form_score"],
            engineered["weekend_readiness"],
            engineered["driver_season_momentum"],
            engineered["driver_recent_improvement"],
            engineered["driver_consistency_score"],
        ]

        arr = np.array(row).reshape(1, -1)
        pred = float(np.clip(MODEL.predict(arr)[0], 1, 20))

        return jsonify({
            "prediction": round(pred, 2),
            "used_features": dict(zip(FEATURE_COLUMNS, row)),
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)