import os
import random
from datetime import timedelta

import pandas as pd
from faker import Faker


# ============================================================
# Project: Enterprise Banking Data Warehouse
# Module: Fraud Alerts
# Description: Generates realistic fraud alert data
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/raw/transactions.csv"
OUTPUT_FILE = "data/raw/fraud_alerts.csv"

ALERT_RATE = 0.05
RANDOM_SEED = 42

fake = Faker()
fake.seed_instance(RANDOM_SEED)
random.seed(RANDOM_SEED)


# ============================================================
# HELPER FUNCTION
# ============================================================

def print_header(title):
    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


# ============================================================
# READ TRANSACTIONS
# ============================================================

print_header("READING TRANSACTIONS DATA")

if not os.path.exists(INPUT_FILE):
    print(f"ERROR: Transaction file not found: {INPUT_FILE}")
    raise SystemExit(1)

try:
    transactions = pd.read_csv(INPUT_FILE)
except Exception as e:
    print("ERROR: Unable to read transactions CSV.")
    print(e)
    raise SystemExit(1)

print("Transactions Loaded Successfully")
print(f"Total Transactions : {len(transactions):,}")


# ============================================================
# REQUIRED COLUMN VALIDATION
# ============================================================

required_columns = [
    "transaction_id",
    "account_id",
    "customer_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "currency",
    "transaction_status",
    "channel",
    "description",
]


missing_columns = [
    column
    for column in required_columns
    if column not in transactions.columns
]


if missing_columns:
    print()
    print("ERROR: Missing required transaction columns:")

    for column in missing_columns:
        print(f" - {column}")

    raise SystemExit(1)


print()
print("Required Transaction Columns Validation Passed")


# ============================================================
# DATA TYPE CONVERSION
# ============================================================

transactions["transaction_id"] = pd.to_numeric(
    transactions["transaction_id"],
    errors="coerce"
)

transactions["account_id"] = pd.to_numeric(
    transactions["account_id"],
    errors="coerce"
)

transactions["customer_id"] = pd.to_numeric(
    transactions["customer_id"],
    errors="coerce"
)

transactions["amount"] = pd.to_numeric(
    transactions["amount"],
    errors="coerce"
)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)


# ============================================================
# CLEAN TRANSACTION DATA
# ============================================================

transactions = transactions.dropna(
    subset=[
        "transaction_id",
        "account_id",
        "customer_id",
        "transaction_date",
        "amount",
    ]
).copy()

transactions = transactions[
    transactions["amount"] > 0
].copy()


print()
print(
    f"Valid Transactions Available : "
    f"{len(transactions):,}"
)


if transactions.empty:
    print("ERROR: No valid transactions available.")
    raise SystemExit(1)


# ============================================================
# SELECT TRANSACTIONS FOR FRAUD ALERTS
# ============================================================

alert_count = max(
    1,
    int(len(transactions) * ALERT_RATE)
)

alert_count = min(
    alert_count,
    len(transactions)
)


alert_transactions = transactions.sample(
    n=alert_count,
    random_state=RANDOM_SEED
).copy()


alert_transactions = alert_transactions.sort_values(
    by=[
        "transaction_date",
        "transaction_id"
    ]
).reset_index(drop=True)


print()
print(
    f"Fraud Alerts To Generate : "
    f"{len(alert_transactions):,}"
)


# ============================================================
# FRAUD ALERT VALUES
# ============================================================

alert_types = [
    "Suspicious Transaction",
    "Large Transaction",
    "Unusual Transaction Pattern",
    "Unusual Location",
    "Rapid Transaction Activity",
    "High Risk Activity",
]

alert_type_weights = [
    25,
    20,
    20,
    10,
    15,
    10,
]


alert_statuses = [
    "Open",
    "Investigating",
    "Resolved",
    "Dismissed",
]

alert_status_weights = [
    30,
    25,
    30,
    15,
]


investigators = [
    "AML Analyst",
    "Fraud Analyst",
    "Risk Analyst",
    "Compliance Analyst",
]


# ============================================================
# GENERATE FRAUD ALERTS
# ============================================================

print_header("GENERATING FRAUD ALERTS")


fraud_alerts = []


for index, transaction in alert_transactions.iterrows():

    alert_id = index + 1

    transaction_id = int(
        transaction["transaction_id"]
    )

    customer_id = int(
        transaction["customer_id"]
    )

    transaction_date = transaction[
        "transaction_date"
    ]

    transaction_type = str(
        transaction["transaction_type"]
    )

    transaction_channel = str(
        transaction["channel"]
    )

    transaction_amount = float(
        transaction["amount"]
    )


    # --------------------------------------------------------
    # CALCULATE RISK SCORE
    # --------------------------------------------------------

    if transaction_amount >= 25000:

        risk_score = random.randint(
            85,
            100
        )

    elif transaction_amount >= 10000:

        risk_score = random.randint(
            70,
            95
        )

    elif transaction_amount >= 5000:

        risk_score = random.randint(
            55,
            85
        )

    else:

        risk_score = random.randint(
            30,
            75
        )


    if transaction_type in [
        "Transfer",
        "Withdrawal",
        "Payment",
    ]:

        risk_score += random.randint(
            0,
            10
        )


    risk_score = min(
        risk_score,
        100
    )


    # --------------------------------------------------------
    # ALERT TYPE
    # --------------------------------------------------------

    alert_type = random.choices(
        alert_types,
        weights=alert_type_weights,
        k=1
    )[0]


    # --------------------------------------------------------
    # ALERT STATUS
    # --------------------------------------------------------

    alert_status = random.choices(
        alert_statuses,
        weights=alert_status_weights,
        k=1
    )[0]


    # --------------------------------------------------------
    # ALERT DESCRIPTION
    # --------------------------------------------------------

    if alert_type == "Large Transaction":

        alert_description = (
            f"Large {transaction_type.lower()} "
            f"transaction of "
            f"${transaction_amount:,.2f} detected "
            f"through {transaction_channel}."
        )

    elif alert_type == "Suspicious Transaction":

        alert_description = (
            f"Suspicious "
            f"{transaction_type.lower()} transaction "
            f"of ${transaction_amount:,.2f} detected."
        )

    elif alert_type == "Unusual Transaction Pattern":

        alert_description = (
            "Transaction pattern appears unusual "
            "compared with expected customer activity."
        )

    elif alert_type == "Unusual Location":

        alert_description = (
            "Transaction originated from a location "
            "that may require additional review."
        )

    elif alert_type == "Rapid Transaction Activity":

        alert_description = (
            "Multiple transaction activities detected "
            "within a short period."
        )

    else:

        alert_description = (
            "Transaction activity identified as "
            "potentially high risk and requires review."
        )


    # --------------------------------------------------------
    # DETECTED TIME
    # --------------------------------------------------------

    detected_time = (
        transaction_date
        + timedelta(
            minutes=random.randint(1, 60)
        )
    )


    # --------------------------------------------------------
    # INVESTIGATION INFORMATION
    # --------------------------------------------------------

    if alert_status in [
        "Investigating",
        "Resolved",
        "Dismissed",
    ]:

        investigated_by = random.choice(
            investigators
        )

    else:

        investigated_by = None


    # --------------------------------------------------------
    # INVESTIGATION NOTES
    # --------------------------------------------------------

    if alert_status == "Resolved":

        investigation_notes = random.choice(
            [
                "Transaction reviewed and confirmed as legitimate.",
                "Customer activity verified successfully.",
                "Alert investigated and resolved without fraud confirmation.",
                "Transaction history reviewed and no fraud identified.",
            ]
        )

    elif alert_status == "Dismissed":

        investigation_notes = random.choice(
            [
                "Alert dismissed after analyst review.",
                "Activity determined to be legitimate.",
                "False positive confirmed after investigation.",
            ]
        )

    elif alert_status == "Investigating":

        investigation_notes = random.choice(
            [
                "Investigation in progress.",
                "Additional transaction activity is being reviewed.",
                "Customer activity requires further analysis.",
            ]
        )

    else:

        investigation_notes = None


    # --------------------------------------------------------
    # RESOLVED TIME
    # --------------------------------------------------------

    if alert_status in [
        "Resolved",
        "Dismissed",
    ]:

        resolved_time = (
            detected_time
            + timedelta(
                days=random.randint(1, 10),
                hours=random.randint(1, 12),
                minutes=random.randint(1, 59),
            )
        )

    else:

        resolved_time = None


    # --------------------------------------------------------
    # CREATE ALERT RECORD
    # --------------------------------------------------------

    fraud_alerts.append(
        {
            "alert_id": alert_id,
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "alert_type": alert_type,
            "risk_score": risk_score,
            "alert_status": alert_status,
            "alert_description": alert_description,
            "detected_time": detected_time,
            "investigated_by": investigated_by,
            "investigation_notes": investigation_notes,
            "resolved_time": resolved_time,
        }
    )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    fraud_alerts
)


# ============================================================
# DATA VALIDATION
# ============================================================

print_header("FRAUD ALERT DATA VALIDATION")


print(
    f"Total Fraud Alerts : "
    f"{len(df):,}"
)


# ============================================================
# REQUIRED OUTPUT COLUMNS
# ============================================================

required_output_columns = [
    "alert_id",
    "transaction_id",
    "customer_id",
    "alert_type",
]


missing_output_columns = [
    column
    for column in required_output_columns
    if column not in df.columns
]


print()
print(
    "Missing Fraud Alert Columns :",
    missing_output_columns
)


if missing_output_columns:
    print()
    print(
        "ERROR: Required fraud alert columns are missing."
    )
    raise SystemExit(1)


# ============================================================
# DUPLICATE VALIDATION
# ============================================================

duplicate_alert_ids = int(
    df["alert_id"].duplicated().sum()
)

duplicate_transaction_ids = int(
    df["transaction_id"].duplicated().sum()
)


print()
print(
    "Duplicate Alert IDs :",
    duplicate_alert_ids
)

print(
    "Duplicate Transaction IDs :",
    duplicate_transaction_ids
)


# ============================================================
# NULL VALIDATION
# ============================================================

required_alert_columns = [
    "alert_id",
    "transaction_id",
    "customer_id",
    "alert_type",
]


total_required_nulls = int(
    df[
        required_alert_columns
    ].isnull().sum().sum()
)


print()
print(
    "NULL Values in Required Columns :",
    total_required_nulls
)


# ============================================================
# RISK SCORE VALIDATION
# ============================================================

invalid_risk_scores = int(
    (
        (df["risk_score"] < 0)
        |
        (df["risk_score"] > 100)
    ).sum()
)


print(
    "Invalid Risk Scores :",
    invalid_risk_scores
)


# ============================================================
# TRANSACTION REFERENCE VALIDATION
# ============================================================

valid_transaction_ids = set(
    transactions[
        "transaction_id"
    ].astype(int)
)


invalid_transaction_references = int(
    (
        ~df[
            "transaction_id"
        ]
        .astype(int)
        .isin(valid_transaction_ids)
    ).sum()
)


print(
    "Invalid Transaction References :",
    invalid_transaction_references
)


# ============================================================
# CUSTOMER REFERENCE VALIDATION
# ============================================================

valid_customer_ids = set(
    transactions[
        "customer_id"
    ].astype(int)
)


invalid_customer_references = int(
    (
        ~df[
            "customer_id"
        ]
        .astype(int)
        .isin(valid_customer_ids)
    ).sum()
)


print(
    "Invalid Customer References :",
    invalid_customer_references
)


# ============================================================
# RESOLVED DATE VALIDATION
# ============================================================

invalid_resolved_dates = int(
    (
        df["resolved_time"].notnull()
        &
        (
            df["resolved_time"]
            < df["detected_time"]
        )
    ).sum()
)


print(
    "Invalid Resolved Dates :",
    invalid_resolved_dates
)


# ============================================================
# DISPLAY SAMPLE DATA
# ============================================================

print_header("SAMPLE FRAUD ALERTS")

print(
    df.head(10).to_string(
        index=False
    )
)


# ============================================================
# ALERT TYPE DISTRIBUTION
# ============================================================

print_header(
    "ALERT TYPE DISTRIBUTION"
)

print(
    df[
        "alert_type"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# ALERT STATUS DISTRIBUTION
# ============================================================

print_header(
    "ALERT STATUS DISTRIBUTION"
)

print(
    df[
        "alert_status"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# FINAL VALIDATION
# ============================================================

validation_passed = (
    len(df) > 0
    and len(missing_output_columns) == 0
    and duplicate_alert_ids == 0
    and total_required_nulls == 0
    and invalid_risk_scores == 0
    and invalid_transaction_references == 0
    and invalid_customer_references == 0
    and invalid_resolved_dates == 0
)


if not validation_passed:

    print()
    print("=" * 65)
    print("FRAUD ALERT DATA VALIDATION FAILED")
    print("=" * 65)

    raise SystemExit(1)


print()
print("=" * 65)
print("FRAUD ALERT DATA VALIDATION PASSED")
print("=" * 65)


# ============================================================
# SAVE CSV
# ============================================================

output_directory = os.path.dirname(
    OUTPUT_FILE
)

if output_directory:

    os.makedirs(
        output_directory,
        exist_ok=True
    )


df.to_csv(
    OUTPUT_FILE,
    index=False,
    date_format="%Y-%m-%d %H:%M:%S"
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 65)
print("FRAUD ALERTS CSV GENERATED SUCCESSFULLY")
print("=" * 65)

print()
print("File :", OUTPUT_FILE)
print("Rows :", len(df))

print()
print("Fraud Alert Generation Completed")
print("=" * 65)