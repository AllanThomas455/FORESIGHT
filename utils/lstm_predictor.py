import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCALER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "lstm_scaler.pkl"
)

lstm_scaler = joblib.load(SCALER_PATH)

LSTM_FEATURES = [
    "units_sold",
    "unit_price",
    "promo_flag",
    "product_age_days",
    "day_of_week",
    "month",
    "is_weekend"
]

SEQUENCE_LENGTH = 30


def predict_lstm_demand(sku_data):

    if len(sku_data) < SEQUENCE_LENGTH:
        raise ValueError(
            "At least 30 days of historical data are required."
        )

    missing_columns = [
        column
        for column in LSTM_FEATURES
        if column not in sku_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Use recent demand as a fallback prediction
    recent_units = (
        sku_data["units_sold"]
        .tail(SEQUENCE_LENGTH)
        .mean()
    )

    prediction = float(recent_units)

    return max(0, prediction)


def get_demand_category(predicted_units):

    if predicted_units <= 5:
        return "Low"
    elif predicted_units <= 10:
        return "Medium"
    elif predicted_units <= 20:
        return "High"
    else:
        return "Very High"