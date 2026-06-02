# Esra Frontend

This folder contains the frontend part of the F1 race finish prediction project.

## What it does

- Takes user input for race prediction features.
- Sends a `POST` request to `/api/predict`.
- Shows the predicted finish position.
- Draws a simple bar chart with the inputs and prediction.
- Displays selected project report charts from the `reports/` folder.

## Expected API contract

Request:

```json
{
  "grid": 4,
  "weekend_readiness": 5.9,
  "last_3_race_avg_finish": 5.9,
  "last_5_race_avg_finish": 7.1,
  "driver_form_score": 6.26,
  "driver_season_momentum": 13.4
}
```

Response:

```json
{
  "predicted_finish_position": 5.72
}
```

If the backend API is not running yet, the page uses a demo fallback so the UI
can still be tested.
