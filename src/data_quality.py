import os
import pandas as pd


# ============================================================
# PROJECT FORESIGHT - DATA QUALITY VALIDATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "raw"
)


# ------------------------------------------------------------
# Load datasets
# ------------------------------------------------------------

sales = pd.read_csv(
    os.path.join(DATA_DIR, "sales_daily.csv")
)

sku_master = pd.read_csv(
    os.path.join(DATA_DIR, "sku_master.csv")
)

calendar = pd.read_csv(
    os.path.join(DATA_DIR, "calendar.csv")
)

inventory = pd.read_csv(
    os.path.join(DATA_DIR, "inventory_snapshots.csv")
)


# ------------------------------------------------------------
# Convert dates
# ------------------------------------------------------------

sales["date"] = pd.to_datetime(sales["date"])
sku_master["launch_date"] = pd.to_datetime(
    sku_master["launch_date"]
)
calendar["date"] = pd.to_datetime(calendar["date"])
inventory["date"] = pd.to_datetime(inventory["date"])


# ============================================================
# HELPER FUNCTION
# ============================================================

def check_dataset(name, df):

    print("\n" + "=" * 70)
    print(f"{name.upper()} DATA QUALITY REPORT")
    print("=" * 70)

    print("\nRows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumns:")
    print(list(df.columns))

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\nMissing values:")

    missing = df.isnull().sum()

    if missing.sum() == 0:
        print("✓ No missing values")
    else:
        print(
            missing[
                missing > 0
            ]
        )

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicates = df.duplicated().sum()

    print(
        "\nDuplicate rows:",
        duplicates
    )

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\nData types:")

    print(df.dtypes)

    # --------------------------------------------------------
    # Numeric summary
    # --------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:

        print("\nNumeric summary:")

        print(
            df[numeric_columns].describe().round(2)
        )


# ============================================================
# RUN QUALITY CHECKS
# ============================================================

check_dataset(
    "Sales Daily",
    sales
)

check_dataset(
    "SKU Master",
    sku_master
)

check_dataset(
    "Calendar",
    calendar
)

check_dataset(
    "Inventory Snapshots",
    inventory
)


# ============================================================
# BUSINESS VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("BUSINESS VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# Sales validation
# ------------------------------------------------------------

print("\n1. SALES VALIDATION")

negative_units = (
    sales["units_sold"] < 0
).sum()

negative_revenue = (
    sales["revenue"] < 0
).sum()

negative_price = (
    sales["unit_price"] < 0
).sum()

print(
    "Negative units:",
    negative_units
)

print(
    "Negative revenue:",
    negative_revenue
)

print(
    "Negative prices:",
    negative_price
)


# ------------------------------------------------------------
# SKU validation
# ------------------------------------------------------------

print("\n2. SKU VALIDATION")

sales_skus = set(
    sales["sku_id"].unique()
)

master_skus = set(
    sku_master["sku_id"].unique()
)

missing_skus = sales_skus - master_skus

print(
    "SKUs in sales:",
    len(sales_skus)
)

print(
    "SKUs in master:",
    len(master_skus)
)

print(
    "Sales SKUs missing from master:",
    len(missing_skus)
)


# ------------------------------------------------------------
# Inventory validation
# ------------------------------------------------------------

print("\n3. INVENTORY VALIDATION")

negative_inventory = (
    inventory["on_hand_units"] < 0
).sum()

negative_orders = (
    inventory["on_order_units"] < 0
).sum()

negative_lead_time = (
    inventory["lead_time_days"] <= 0
).sum()

negative_reorder = (
    inventory["reorder_point"] < 0
).sum()

print(
    "Negative on-hand inventory:",
    negative_inventory
)

print(
    "Negative on-order inventory:",
    negative_orders
)

print(
    "Invalid lead times:",
    negative_lead_time
)

print(
    "Negative reorder points:",
    negative_reorder
)


# ------------------------------------------------------------
# Calendar validation
# ------------------------------------------------------------

print("\n4. CALENDAR VALIDATION")

print(
    "Calendar start:",
    calendar["date"].min().date()
)

print(
    "Calendar end:",
    calendar["date"].max().date()
)

print(
    "Calendar days:",
    calendar["date"].nunique()
)

expected_days = (
    calendar["date"].max()
    - calendar["date"].min()
).days + 1

print(
    "Expected days:",
    expected_days
)

if (
    calendar["date"].nunique()
    == expected_days
):

    print(
        "✓ Calendar has continuous dates"
    )

else:

    print(
        "⚠ Calendar has missing dates"
    )


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("DATA QUALITY CHECK COMPLETE")
print("=" * 70)

print(
    "\n✓ All four datasets loaded successfully."
)

print(
    "✓ Data quality validation completed."
)

print(
    "✓ Business validation completed."
)

print(
    "\nNext stage: Exploratory Data Analysis (EDA)"
)

print("=" * 70)