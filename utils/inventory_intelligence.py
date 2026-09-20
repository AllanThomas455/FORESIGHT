import math


def calculate_inventory_intelligence(
    predicted_units,
    rolling_mean_7,
    rolling_mean_30,
    rolling_std_7,
    lead_time_days=7,
    safety_factor=1.65
):
    """
    Calculate inventory intelligence metrics using demand forecasting
    and historical demand behaviour.

    IMPORTANT:
    The current dataset does not contain actual stock-on-hand data.
    Therefore, this module provides demand-based inventory risk estimates
    rather than claiming to measure actual stockout or overstock conditions.
    """

    # ---------------------------------------------------------
    # Clean and protect input values
    # ---------------------------------------------------------

    predicted_units = max(0.0, float(predicted_units or 0))
    rolling_mean_7 = max(0.0, float(rolling_mean_7 or 0))
    rolling_mean_30 = max(0.0, float(rolling_mean_30 or 0))
    rolling_std_7 = max(0.0, float(rolling_std_7 or 0))

    lead_time_days = max(1, int(lead_time_days))
    safety_factor = max(0.0, float(safety_factor))

    # ---------------------------------------------------------
    # Demand trend
    # ---------------------------------------------------------

    if rolling_mean_30 > 0:
        demand_change_pct = (
            (rolling_mean_7 - rolling_mean_30)
            / rolling_mean_30
        ) * 100
    else:
        demand_change_pct = 0.0

    # ---------------------------------------------------------
    # Forecast pressure
    # ---------------------------------------------------------

    if rolling_mean_7 > 0:
        forecast_vs_recent_pct = (
            (predicted_units - rolling_mean_7)
            / rolling_mean_7
        ) * 100
    else:
        forecast_vs_recent_pct = 0.0

    # ---------------------------------------------------------
    # Estimated safety stock
    #
    # Safety stock is based on recent demand volatility and
    # the assumed replenishment lead time.
    # ---------------------------------------------------------

    safety_stock = (
        safety_factor
        * rolling_std_7
        * math.sqrt(lead_time_days)
    )

    # ---------------------------------------------------------
    # Estimated inventory target
    #
    # Forecast demand during lead time + safety stock.
    # ---------------------------------------------------------

    lead_time_demand = predicted_units * lead_time_days

    recommended_inventory_target = (
        lead_time_demand + safety_stock
    )

    # ---------------------------------------------------------
    # Demand volatility percentage
    # ---------------------------------------------------------

    if rolling_mean_7 > 0:
        volatility_pct = (
            rolling_std_7 / rolling_mean_7
        ) * 100
    else:
        volatility_pct = 0.0

    # ---------------------------------------------------------
    # Determine demand trend
    # ---------------------------------------------------------

    if demand_change_pct >= 15:
        demand_trend = "Increasing"
    elif demand_change_pct <= -15:
        demand_trend = "Decreasing"
    else:
        demand_trend = "Stable"

    # ---------------------------------------------------------
    # Determine demand pressure
    # ---------------------------------------------------------

    if forecast_vs_recent_pct >= 20:
        demand_pressure = "High"
    elif forecast_vs_recent_pct >= 10:
        demand_pressure = "Moderate"
    elif forecast_vs_recent_pct <= -20:
        demand_pressure = "Low"
    else:
        demand_pressure = "Normal"

    # ---------------------------------------------------------
    # Determine risk level
    #
    # This is a demand-based inventory risk estimate.
    # ---------------------------------------------------------

    risk_score = 0

    # Increasing demand
    if demand_change_pct >= 20:
        risk_score += 2
    elif demand_change_pct >= 10:
        risk_score += 1

    # Forecast above recent demand
    if forecast_vs_recent_pct >= 25:
        risk_score += 2
    elif forecast_vs_recent_pct >= 10:
        risk_score += 1

    # High volatility
    if volatility_pct >= 50:
        risk_score += 2
    elif volatility_pct >= 30:
        risk_score += 1

    # High absolute forecast
    if predicted_units >= 20:
        risk_score += 1

    if risk_score >= 5:
        risk_level = "High"
        risk_type = "Stockout Risk"
    elif risk_score >= 3:
        risk_level = "Moderate"
        risk_type = "Demand Pressure"
    else:
        risk_level = "Low"
        risk_type = "Stable Demand"

    # ---------------------------------------------------------
    # Inventory recommendation
    # ---------------------------------------------------------

    if risk_level == "High":
        recommendation = (
            "Increase inventory coverage and prioritize replenishment. "
            "Demand is showing elevated pressure or volatility."
        )

    elif risk_level == "Moderate":
        recommendation = (
            "Monitor inventory closely and maintain additional safety stock "
            "to handle possible demand increases."
        )

    else:
        recommendation = (
            "Maintain normal inventory coverage and continue monitoring "
            "recent demand behaviour."
        )

    # ---------------------------------------------------------
    # Return all intelligence metrics
    # ---------------------------------------------------------

    return {
        "predicted_units": round(predicted_units, 2),
        "rolling_mean_7": round(rolling_mean_7, 2),
        "rolling_mean_30": round(rolling_mean_30, 2),
        "rolling_std_7": round(rolling_std_7, 2),
        "demand_change_pct": round(demand_change_pct, 2),
        "forecast_vs_recent_pct": round(forecast_vs_recent_pct, 2),
        "volatility_pct": round(volatility_pct, 2),
        "lead_time_days": lead_time_days,
        "safety_factor": round(safety_factor, 2),
        "safety_stock": round(safety_stock, 2),
        "lead_time_demand": round(lead_time_demand, 2),
        "recommended_inventory_target": round(
            recommended_inventory_target,
            2
        ),
        "demand_trend": demand_trend,
        "demand_pressure": demand_pressure,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_type": risk_type,
        "recommendation": recommendation,
        "data_limitation": (
            "Inventory risk is estimated from demand behaviour because "
            "the dataset does not contain actual stock-on-hand quantities."
        )
    }