from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import math

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


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    data = pd.read_csv(DATA_PATH)

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data["sku_id"] = data["sku_id"].astype(str)

    return data


# ============================================================
# INVENTORY INTELLIGENCE
# ============================================================

def calculate_inventory_intelligence(
    sku_data,
    predicted_units,
    lead_time_days=7,
    safety_factor=1.65
):

    sku_data = sku_data.sort_values("date").copy()

    rolling_mean_7 = (
        sku_data["units_sold"]
        .tail(7)
        .mean()
    )

    rolling_mean_30 = (
        sku_data["units_sold"]
        .tail(30)
        .mean()
    )

    rolling_std_7 = (
        sku_data["units_sold"]
        .tail(7)
        .std()
    )

    if pd.isna(rolling_std_7):
        rolling_std_7 = 0.0

    if rolling_mean_7 <= 0:
        rolling_mean_7 = 0.01

    if rolling_mean_30 <= 0:
        rolling_mean_30 = 0.01

    demand_change_pct = (
        (rolling_mean_7 - rolling_mean_30)
        / rolling_mean_30
    ) * 100

    forecast_vs_recent_pct = (
        (predicted_units - rolling_mean_7)
        / rolling_mean_7
    ) * 100

    if demand_change_pct > 10:
        demand_trend = "Increasing"
    elif demand_change_pct < -10:
        demand_trend = "Decreasing"
    else:
        demand_trend = "Stable"

    if forecast_vs_recent_pct > 20:
        demand_pressure = "High"
    elif forecast_vs_recent_pct > 10:
        demand_pressure = "Elevated"
    elif forecast_vs_recent_pct < -20:
        demand_pressure = "Low"
    else:
        demand_pressure = "Normal"

    lead_time_demand = (
        predicted_units * lead_time_days
    )

    safety_stock = (
        rolling_std_7
        * safety_factor
        * math.sqrt(lead_time_days)
    )

    recommended_inventory_target = (
        lead_time_demand
        + safety_stock
    )

    volatility_pct = (
        rolling_std_7
        / rolling_mean_7
    ) * 100

    risk_score = 0

    if demand_change_pct > 20:
        risk_score += 2
    elif demand_change_pct > 10:
        risk_score += 1

    if forecast_vs_recent_pct > 20:
        risk_score += 2
    elif forecast_vs_recent_pct > 10:
        risk_score += 1

    if volatility_pct > 40:
        risk_score += 2
    elif volatility_pct > 25:
        risk_score += 1

    if risk_score >= 4:
        risk_level = "High"
    elif risk_score >= 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if risk_level == "High":

        if volatility_pct > 40:
            risk_type = "High Demand Volatility"

        elif demand_trend == "Increasing":
            risk_type = "Rising Demand Risk"

        else:
            risk_type = "Inventory Pressure"

    elif risk_level == "Medium":

        if demand_trend == "Increasing":
            risk_type = "Increasing Demand"

        elif volatility_pct > 25:
            risk_type = "Demand Volatility"

        else:
            risk_type = "Moderate Inventory Risk"

    else:
        risk_type = "Stable Demand"

    if risk_level == "High":

        recommendation = (
            "Increase inventory coverage and closely monitor "
            "demand to reduce the risk of stockouts."
        )

    elif risk_level == "Medium":

        recommendation = (
            "Consider maintaining additional inventory coverage "
            "while monitoring recent demand behaviour."
        )

    else:

        recommendation = (
            "Maintain normal inventory coverage and continue "
            "monitoring recent demand behaviour."
        )

    return {

        "risk_level": risk_level,

        "risk_score": int(
            risk_score
        ),

        "risk_type": risk_type,

        "demand_trend": demand_trend,

        "demand_pressure": demand_pressure,

        "demand_change_pct": round(
            demand_change_pct,
            2
        ),

        "forecast_vs_recent_pct": round(
            forecast_vs_recent_pct,
            2
        ),

        "lead_time_days": lead_time_days,

        "lead_time_demand": round(
            lead_time_demand,
            2
        ),

        "safety_factor": safety_factor,

        "safety_stock": round(
            safety_stock,
            2
        ),

        "recommended_inventory_target": round(
            recommended_inventory_target,
            2
        ),

        "volatility_pct": round(
            volatility_pct,
            2
        ),

        "rolling_mean_7": round(
            rolling_mean_7,
            2
        ),

        "rolling_mean_30": round(
            rolling_mean_30,
            2
        ),

        "rolling_std_7": round(
            rolling_std_7,
            2
        ),

        "predicted_units": round(
            predicted_units,
            2
        ),

        "data_limitation": (
            "Inventory risk is estimated from demand behaviour "
            "because the dataset does not contain actual "
            "stock-on-hand quantities."
        ),

        "recommendation": recommendation
    }


# ============================================================
# HOME DASHBOARD
# ============================================================

@app.route("/")
def home():

    data = load_data()

    skus = sorted(
        data["sku_id"]
        .dropna()
        .unique()
        .tolist()
    )

    return render_template(
        "index.html",
        skus=skus
    )


# ============================================================
# ANALYTICS API
# ============================================================

@app.route("/analytics")
def analytics():

    data = load_data()

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

    first_date = data["date"].min()

    latest_date = data["date"].max()

    data_period_days = (
        latest_date - first_date
    ).days + 1

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

    top_category_row = category.iloc[0]

    top_category = (
        top_category_row["category"]
    )

    top_category_units = int(
        top_category_row["units"]
    )

    highest_month_row = monthly.loc[
        monthly["units"].idxmax()
    ]

    highest_month = (
        highest_month_row["date"]
    )

    highest_month_units = int(
        highest_month_row["units"]
    )

    lowest_month_row = monthly.loc[
        monthly["units"].idxmin()
    ]

    lowest_month = (
        lowest_month_row["date"]
    )

    lowest_month_units = int(
        lowest_month_row["units"]
    )

    dominant_demand = (
        demand_distribution.idxmax()
    )

    dominant_demand_count = int(
        demand_distribution.max()
    )

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

    data_coverage = {

        "first_date":
            first_date.strftime(
                "%Y-%m-%d"
            ),

        "latest_date":
            latest_date.strftime(
                "%Y-%m-%d"
            ),

        "display_start":
            first_date.strftime(
                "%d %b %Y"
            ),

        "display_end":
            latest_date.strftime(
                "%d %b %Y"
            ),

        "data_period_days":
            data_period_days,

        "forecast_note":
            "Forecasts are generated from the latest "
            "available historical data."
    }

    return jsonify({

        "monthly":
            monthly.to_dict(
                orient="records"
            ),

        "category":
            category.to_dict(
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

        "latest_date":
            latest_date.strftime(
                "%Y-%m-%d"
            ),

        "data_coverage":
            data_coverage,

        "kpis": {

            "total_units":
                total_units,

            "total_revenue":
                total_revenue,

            "average_unit_price":
                average_unit_price,

            "unique_skus":
                unique_skus
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


# ============================================================
# DEMAND + INVENTORY PREDICTION API
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        data = load_data()

        request_data = request.get_json(
            silent=True
        )

        if not request_data:

            return jsonify({
                "error":
                    "No prediction data received."
            }), 400

        sku = str(
            request_data.get(
                "sku",
                ""
            )
        ).strip()

        if not sku:

            return jsonify({
                "error":
                    "Please select an SKU first."
            }), 400

        available_skus = set(
            data["sku_id"]
            .astype(str)
            .str.strip()
            .unique()
        )

        if sku not in available_skus:

            return jsonify({
                "error":
                    "Invalid SKU selected: " + sku
            }), 400

        sku_data = (
            data[
                data["sku_id"]
                .astype(str)
                .str.strip()
                == sku
            ]
            .sort_values("date")
            .copy()
        )

        if sku_data.empty:

            return jsonify({
                "error":
                    "No historical data found for " + sku
            }), 400

        prediction = predict_lstm_demand(
            sku_data
        )

        predicted_units = max(
            0,
            round(
                float(prediction)
            )
        )

        demand_category = (
            get_demand_category(
                predicted_units
            )
        )

        last_date = (
            sku_data["date"].max()
        )

        forecast_date = (
            last_date
            + pd.Timedelta(days=1)
        )

        inventory_intelligence = (
            calculate_inventory_intelligence(
                sku_data=sku_data,
                predicted_units=float(
                    prediction
                )
            )
        )

        return jsonify({

            "success": True,

            "sku":
                sku,

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
                demand_category,

            "inventory_intelligence":
                inventory_intelligence
        })

    except Exception as error:

        print(
            "\n========== PREDICTION ERROR =========="
        )

        print(
            repr(error)
        )

        print(
            "======================================\n"
        )

        return jsonify({
            "error":
                "Prediction failed: " + str(error)
        }), 500


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )