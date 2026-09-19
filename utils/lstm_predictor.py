import os
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "lstm_demand_model.keras"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "lstm_scaler.pkl"
)


# --------------------------------------------------
# Load trained model and scaler
# --------------------------------------------------

lstm_model = load_model(MODEL_PATH)
lstm_scaler = joblib.load(SCALER_PATH)


# --------------------------------------------------
# LSTM configuration
# --------------------------------------------------

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


# --------------------------------------------------
# Prediction function
# --------------------------------------------------

def predict_lstm_demand(sku_data):
    """
    Predict next-day demand for a SKU.

    sku_data must contain at least the latest
    30 observations with the required LSTM features.
    """

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

    sequence = (
        sku_data[LSTM_FEATURES]
        .tail(SEQUENCE_LENGTH)
        .values
    )

    sequence_scaled = lstm_scaler.transform(sequence)

    sequence_scaled = sequence_scaled.reshape(
        1,
        SEQUENCE_LENGTH,
        len(LSTM_FEATURES)
    )

    prediction = lstm_model.predict(
        sequence_scaled,
        verbose=0
    )[0][0]

    return max(0, float(prediction))


# --------------------------------------------------
# Demand category
# --------------------------------------------------

def get_demand_category(predicted_units):
    """
    Convert predicted demand into a business-friendly
    demand category.
    """

    if predicted_units <= 5:
        return "Low"

    elif predicted_units <= 10:
        return "Medium"

    elif predicted_units <= 20:
        return "High"

    else:
        return "Very High"