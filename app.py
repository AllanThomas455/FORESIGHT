from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

from utils.lstm_predictor import (
    predict_lstm_demand,
    get_demand_category
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "model_data.csv"
)


# ==========================================
# LOAD DATA
# ==========================================

def load_data():

    data = pd.read_csv(DATA_PATH)

    data["date"] = pd.to_datetime(
        data["date"]
    )

    return data


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    data = load_data()

    skus = sorted(
        data["sku_id"].unique()
    )

    return render_template(
        "index.html",
        skus=skus
    )


# ==========================================
# ANALYTICS API
# ==========================================

@app.route("/analytics")
def analytics():

    data = load_data()

    # --------------------------------------
    # MONTHLY ANALYTICS
    # --------------------------------------

    monthly = (
        data.groupby(
            data["date"].dt.to_period("M")
        )
        .agg(
            units=("units_sold", "sum"),
            revenue=("revenue", "sum")
        )
        .reset_index()
    )

    monthly["date"] = (
        monthly["date"]
        .dt.strftime("%Y-%m")
    )


    # --------------------------------------
    # CATEGORY ANALYTICS
    # --------------------------------------

    category = (
        data.groupby("category")
        .agg(
            units=("units_sold", "sum"),
            revenue=("revenue", "sum")
        )
        .reset_index()
        .sort_values(
            "units",
            ascending=False
        )
    )


    # --------------------------------------
    # DEMAND DISTRIBUTION
    # --------------------------------------

    demand_levels = pd.cut(
        data["units_sold"],
        bins=[
            0,
            5,
            10,
            20,
            float("inf")
        ],
        labels=[
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    )

    demand_distribution = (
        demand_levels
        .value_counts()
        .reindex(
            [
                "Low",
                "Medium",
                "High",
                "Very High"
            ]
        )
        .fillna(0)
    )


    # --------------------------------------
    # LATEST DATE
    # --------------------------------------

    latest_date = data["date"].max()


    # --------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------

    total_units = int(
        data["units_sold"].sum()
    )

    total_revenue = float(
        data["revenue"].sum()
    )

    average_unit_price = float(
        data["unit_price"].mean()
    )

    unique_skus = int(
        data["sku_id"].nunique()
    )


    # --------------------------------------
    # AI INSIGHT 1
    # TOP CATEGORY
    # --------------------------------------

    top_category_row = category.iloc[0]

    top_category = (
        top_category_row["category"]
    )

    top_category_units = int(
        top_category_row["units"]
    )


    # --------------------------------------
    # AI INSIGHT 2
    # HIGHEST DEMAND MONTH
    # --------------------------------------

    highest_month_row = monthly.loc[
        monthly["units"].idxmax()
    ]

    highest_month = (
        highest_month_row["date"]
    )

    highest_month_units = int(
        highest_month_row["units"]
    )


    # --------------------------------------
    # AI INSIGHT 3
    # LOWEST DEMAND MONTH
    # --------------------------------------

    lowest_month_row = monthly.loc[
        monthly["units"].idxmin()
    ]

    lowest_month = (
        lowest_month_row["date"]
    )

    lowest_month_units = int(
        lowest_month_row["units"]
    )


    # --------------------------------------
    # AI INSIGHT 4
    # MOST COMMON DEMAND LEVEL
    # --------------------------------------

    dominant_demand = (
        demand_distribution.idxmax()
    )

    dominant_demand_count = int(
        demand_distribution.max()
    )


    # --------------------------------------
    # AI INSIGHT 5
    # DATA PERIOD
    # --------------------------------------

    first_date = data["date"].min()

    data_period_days = (
        latest_date - first_date
    ).days + 1


    # --------------------------------------
    # MODEL PERFORMANCE
    # --------------------------------------

    model_performance = {
        "models": [
            "MLP",
            "LSTM"
        ],

        "mae": [
            2.5930,
            2.4356
        ],

        "rmse": [
            3.6788,
            3.6284
        ],

        "r2": [
            0.7595,
            0.7661
        ],

        "within_10": 33.28,

        "within_20": 60.59
    }


    # --------------------------------------
    # RETURN ANALYTICS
    # --------------------------------------

    return jsonify({

        "monthly": monthly.to_dict(
            orient="records"
        ),

        "category": category.to_dict(
            orient="records"
        ),

        "demand_distribution": [
            {
                "level": level,
                "count": int(count)
            }
            for level, count
            in demand_distribution.items()
        ],

        "latest_date": latest_date.strftime(
            "%Y-%m-%d"
        ),

        "kpis": {

            "total_units": total_units,

            "total_revenue": total_revenue,

            "average_unit_price":
                average_unit_price,

            "unique_skus": unique_skus
        },

        "insights": {

            "top_category":
                top_category,

            "top_category_units":
                top_category_units,

            "highest_month":
                highest_month,

            "highest_month_units":
                highest_month_units,

            "lowest_month":
                lowest_month,

            "lowest_month_units":
                lowest_month_units,

            "dominant_demand":
                dominant_demand,

            "dominant_demand_count":
                dominant_demand_count,

            "first_date":
                first_date.strftime(
                    "%Y-%m-%d"
                ),

            "latest_date":
                latest_date.strftime(
                    "%Y-%m-%d"
                ),

            "data_period_days":
                data_period_days
        },

        "model_performance":
            model_performance
    })


# ==========================================
# LSTM PREDICTION
# ==========================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    data = load_data()

    request_data = request.get_json()

    # --------------------------------------
    # VALIDATE REQUEST
    # --------------------------------------

    if not request_data:

        return jsonify({
            "error":
                "No prediction data received."
        }), 400


    sku = request_data.get(
        "sku"
    )


    # --------------------------------------
    # VALIDATE SKU
    # --------------------------------------

    if sku not in data["sku_id"].unique():

        return jsonify({
            "error":
                "Invalid SKU selected."
        }), 400


    # --------------------------------------
    # GET SKU HISTORY
    # --------------------------------------

    sku_data = (
        data[
            data["sku_id"] == sku
        ]
        .sort_values("date")
        .copy()
    )


    # --------------------------------------
    # GENERATE PREDICTION
    # --------------------------------------

    prediction = predict_lstm_demand(
        sku_data
    )

    predicted_units = round(
        prediction
    )

    demand_category = get_demand_category(
        predicted_units
    )


    # --------------------------------------
    # FORECAST DATE
    # --------------------------------------

    last_date = sku_data["date"].max()

    forecast_date = (
        last_date +
        pd.Timedelta(days=1)
    )


    # --------------------------------------
    # RETURN PREDICTION
    # --------------------------------------

    return jsonify({

        "sku": sku,

        "last_date":
            last_date.strftime(
                "%Y-%m-%d"
            ),

        "forecast_date":
            forecast_date.strftime(
                "%Y-%m-%d"
            ),

        "predicted_units":
            predicted_units,

        "demand_category":
            demand_category
    })


# ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )


