import os
import numpy as np
import pandas as pd

# ============================================================
# PROJECT FORESIGHT - SYNTHETIC DATA GENERATOR
# ============================================================

# Reproducibility
np.random.seed(42)

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

NUM_SKUS = 100

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "raw"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. SKU MASTER
# ============================================================

categories = {
    "Furniture": [
        "Sofas",
        "Beds",
        "Tables",
        "Chairs"
    ],
    "Home Decor": [
        "Lamps",
        "Rugs",
        "Wall Art",
        "Cushions"
    ],
    "Kitchen": [
        "Cookware",
        "Storage",
        "Appliances",
        "Dinnerware"
    ],
    "Bedding": [
        "Bedsheets",
        "Pillows",
        "Blankets",
        "Mattress Protectors"
    ],
    "Electronics": [
        "Smart Lighting",
        "Speakers",
        "Fans",
        "Accessories"
    ]
}

category_names = list(categories.keys())

sku_rows = []

for i in range(1, NUM_SKUS + 1):

    sku_id = f"SKU{i:03d}"

    category = np.random.choice(category_names)
    subcategory = np.random.choice(categories[category])

    launch_date = pd.Timestamp(
        START_DATE
    ) + pd.Timedelta(days=np.random.randint(0, 365))

    unit_cost = round(
        np.random.uniform(300, 8000),
        2
    )

    markup = np.random.uniform(1.3, 2.2)

    list_price = round(
        unit_cost * markup,
        2
    )

    sku_rows.append({
        "sku_id": sku_id,
        "category": category,
        "subcategory": subcategory,
        "launch_date": launch_date,
        "unit_cost": unit_cost,
        "list_price": list_price
    })

sku_master = pd.DataFrame(sku_rows)


# ============================================================
# 2. CALENDAR
# ============================================================

dates = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="D"
)

calendar = pd.DataFrame({
    "date": dates
})

calendar["week"] = calendar["date"].dt.isocalendar().week.astype(int)
calendar["month"] = calendar["date"].dt.month
calendar["year"] = calendar["date"].dt.year
calendar["day_of_week"] = calendar["date"].dt.dayofweek

# Seasons
def get_season(month):

    if month in [12, 1, 2]:
        return "Winter"

    elif month in [3, 4, 5]:
        return "Spring"

    elif month in [6, 7, 8]:
        return "Summer"

    else:
        return "Autumn"


calendar["season"] = calendar["month"].apply(get_season)

# ------------------------------------------------------------
# Holidays
# ------------------------------------------------------------

holiday_dates = set(pd.to_datetime([
    "2024-01-26",
    "2024-08-15",
    "2024-10-02",
    "2024-10-31",
    "2024-12-25",
    "2025-01-26",
    "2025-08-15",
    "2025-10-02",
    "2025-10-20",
    "2025-12-25"
]))

calendar["is_holiday"] = calendar["date"].isin(
    holiday_dates
).astype(int)


# ============================================================
# PROMOTIONS
# ============================================================

calendar["promo_event"] = "No Promotion"

promotion_periods = [
    ("2024-03-15", "2024-03-25", "Spring Sale"),
    ("2024-06-10", "2024-06-20", "Summer Sale"),
    ("2024-08-10", "2024-08-20", "Independence Sale"),
    ("2024-10-20", "2024-11-05", "Festive Sale"),
    ("2024-11-20", "2024-12-05", "Black Friday"),
    ("2025-03-15", "2025-03-25", "Spring Sale"),
    ("2025-06-10", "2025-06-20", "Summer Sale"),
    ("2025-08-10", "2025-08-20", "Independence Sale"),
    ("2025-10-20", "2025-11-05", "Festive Sale"),
    ("2025-11-20", "2025-12-05", "Black Friday")
]

for start, end, name in promotion_periods:

    mask = (
        (calendar["date"] >= pd.Timestamp(start)) &
        (calendar["date"] <= pd.Timestamp(end))
    )

    calendar.loc[mask, "promo_event"] = name


calendar["promo_flag"] = (
    calendar["promo_event"] != "No Promotion"
).astype(int)


# ============================================================
# 3. DAILY SALES
# ============================================================

sales_rows = []

for _, sku in sku_master.iterrows():

    sku_id = sku["sku_id"]
    category = sku["category"]
    launch_date = sku["launch_date"]

    # Base demand differs by category
    category_demand = {
        "Furniture": 4.5,
        "Home Decor": 7.0,
        "Kitchen": 8.0,
        "Bedding": 6.5,
        "Electronics": 5.5
    }

    base_demand = category_demand[category]

    # SKU-specific demand strength
    sku_factor = np.random.uniform(0.5, 2.0)

    # Random demand trend
    trend = np.random.uniform(
        -0.0002,
        0.0006
    )

    for day_index, current_date in enumerate(dates):

        # Don't generate sales before SKU launch
        if current_date < launch_date:
            continue

        # Weekly seasonality
        day_of_week = current_date.dayofweek

        if day_of_week in [5, 6]:
            weekly_factor = 1.20
        elif day_of_week == 4:
            weekly_factor = 1.10
        else:
            weekly_factor = 0.95

        # Monthly/seasonal effects
        month = current_date.month

        seasonal_factor = 1.0

        if month in [10, 11, 12]:
            seasonal_factor = 1.25
        elif month in [3, 4]:
            seasonal_factor = 1.08
        elif month in [6, 7]:
            seasonal_factor = 0.95

        # Promotion effect
        promo_flag = int(
            current_date in set(
                calendar.loc[
                    calendar["promo_flag"] == 1,
                    "date"
                ]
            )
        )

        promo_factor = 1.0

        if promo_flag:
            promo_factor = 1.50

        # Holiday effect
        holiday_flag = int(
            current_date in holiday_dates
        )

        holiday_factor = 1.0

        if holiday_flag:
            holiday_factor = 1.15

        # Long-term trend
        trend_factor = 1 + (trend * day_index)

        # Expected units
        expected_units = (
            base_demand
            * sku_factor
            * weekly_factor
            * seasonal_factor
            * promo_factor
            * holiday_factor
            * trend_factor
        )

        # Random noise
        noise = np.random.normal(
            0,
            max(expected_units * 0.20, 0.5)
        )

        units_sold = max(
            0,
            round(expected_units + noise)
        )

        # Small probability of unusually high demand
        if np.random.random() < 0.01:
            units_sold = int(
                units_sold * np.random.uniform(1.5, 2.5)
            )

        unit_price = sku["list_price"]

        # Promotional discount
        if promo_flag:
            unit_price *= np.random.uniform(
                0.85,
                0.95
            )

        unit_price = round(
            unit_price,
            2
        )

        revenue = round(
            units_sold * unit_price,
            2
        )

        sales_rows.append({
            "date": current_date,
            "sku_id": sku_id,
            "units_sold": units_sold,
            "revenue": revenue,
            "unit_price": unit_price,
            "promo_flag": promo_flag
        })


sales_daily = pd.DataFrame(sales_rows)


# ============================================================
# 4. INVENTORY SNAPSHOTS
# ============================================================

inventory_rows = []

# Average daily demand per SKU
average_demand = (
    sales_daily
    .groupby("sku_id")["units_sold"]
    .mean()
)

for _, sku in sku_master.iterrows():

    sku_id = sku["sku_id"]

    avg_demand = average_demand.get(
        sku_id,
        5
    )

    # Lead time between 2 and 14 days
    lead_time = np.random.randint(
        2,
        15
    )

    # Reorder point
    reorder_point = max(
        5,
        int(
            avg_demand
            * lead_time
            * np.random.uniform(
                1.0,
                1.4
            )
        )
    )

    # Initial inventory
    initial_inventory = max(
        10,
        int(
            avg_demand
            * np.random.uniform(
                10,
                30
            )
        )
    )

    current_inventory = initial_inventory

    # Generate weekly inventory snapshots
    sku_sales = (
        sales_daily[
            sales_daily["sku_id"] == sku_id
        ]
        .set_index("date")
    )

    for current_date in dates:

        # Only snapshot every 7 days
        if current_date.dayofweek != 6:
            continue

        daily_sales = sku_sales.loc[
            sku_sales.index <= current_date,
            "units_sold"
        ]

        if len(daily_sales) > 0:
            recent_demand = daily_sales.tail(7).sum()
        else:
            recent_demand = avg_demand * 7

        # Inventory consumption
        current_inventory -= int(
            recent_demand * np.random.uniform(
                0.8,
                1.1
            )
        )

        current_inventory = max(
            0,
            current_inventory
        )

        # Incoming inventory
        on_order_units = 0

        if current_inventory <= reorder_point:

            on_order_units = max(
                0,
                int(
                    avg_demand
                    * np.random.uniform(
                        10,
                        25
                    )
                )
            )

            # Some orders arrive immediately
            if np.random.random() < 0.6:
                current_inventory += on_order_units
                on_order_units = 0

        inventory_rows.append({
            "date": current_date,
            "sku_id": sku_id,
            "on_hand_units": int(current_inventory),
            "on_order_units": int(on_order_units),
            "lead_time_days": int(lead_time),
            "reorder_point": int(reorder_point)
        })


inventory_snapshots = pd.DataFrame(
    inventory_rows
)


# ============================================================
# 5. SAVE DATASETS
# ============================================================

sales_daily.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sales_daily.csv"
    ),
    index=False
)

sku_master.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sku_master.csv"
    ),
    index=False
)

calendar.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "calendar.csv"
    ),
    index=False
)

inventory_snapshots.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "inventory_snapshots.csv"
    ),
    index=False
)


# ============================================================
# 6. SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("PROJECT FORESIGHT - DATA GENERATION COMPLETE")
print("=" * 60)

print(f"\nOutput directory:")
print(OUTPUT_DIR)

print("\nFiles created:")

print(
    f"  sales_daily.csv          "
    f"{len(sales_daily):,} rows"
)

print(
    f"  sku_master.csv           "
    f"{len(sku_master):,} rows"
)

print(
    f"  calendar.csv             "
    f"{len(calendar):,} rows"
)

print(
    f"  inventory_snapshots.csv  "
    f"{len(inventory_snapshots):,} rows"
)

print("\nSKU count:", sales_daily["sku_id"].nunique())

print(
    "Sales date range:",
    sales_daily["date"].min().date(),
    "to",
    sales_daily["date"].max().date()
)

print(
    "Total units sold:",
    f"{sales_daily['units_sold'].sum():,}"
)

print(
    "Total revenue:",
    f"₹{sales_daily['revenue'].sum():,.2f}"
)

print("\nData generation successful!")
print("=" * 60)