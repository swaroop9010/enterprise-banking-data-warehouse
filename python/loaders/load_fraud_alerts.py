import os
import sys
import getpass

import pandas as pd
import psycopg2
from psycopg2 import extras


# ============================================================
# PROJECT: ENTERPRISE BANKING DATA WAREHOUSE
# MODULE: FRAUD ALERTS LOADER
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = "data/raw/fraud_alerts.csv"

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "enterprisebankingdw"
DB_USER = "postgres"

TABLE_NAME = "fraud_alerts"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_header(title):
    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


def fail(message, cursor=None, conn=None):
    print()
    print("=" * 65)
    print("ERROR")
    print("=" * 65)
    print(message)
    print("=" * 65)

    try:
        if cursor:
            cursor.close()
    except Exception:
        pass

    try:
        if conn:
            conn.close()
    except Exception:
        pass

    sys.exit(1)


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

print_header("CONNECTING TO POSTGRESQL")

password = getpass.getpass("Enter PostgreSQL password: ")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=password
    )

    conn.autocommit = False

    cursor = conn.cursor()

    print("Database Connected Successfully")

except Exception as e:
    fail(
        f"Unable to connect to PostgreSQL.\n\n{e}"
    )


# ============================================================
# CHECK EXISTING FRAUD ALERTS
# ============================================================

print_header("CHECKING FRAUD ALERT TABLE")

try:

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM fraud_alerts;
        """
    )

    existing_records = cursor.fetchone()[0]

    print(
        f"Existing Fraud Alerts : {existing_records:,}"
    )

except Exception as e:

    conn.rollback()

    fail(
        f"Unable to access fraud_alerts table.\n\n{e}",
        cursor,
        conn
    )


# ============================================================
# READ FRAUD ALERT CSV
# ============================================================

print_header("READING FRAUD ALERTS CSV")

if not os.path.exists(CSV_FILE):

    fail(
        f"Fraud alerts CSV not found:\n{CSV_FILE}",
        cursor,
        conn
    )


try:

    df = pd.read_csv(
        CSV_FILE,
        keep_default_na=True
    )

except Exception as e:

    fail(
        f"Unable to read fraud alerts CSV.\n\n{e}",
        cursor,
        conn
    )


print("Fraud Alerts CSV Loaded Successfully")
print(f"Total Records : {len(df):,}")


# ============================================================
# REQUIRED CSV COLUMNS
# ============================================================

required_columns = [
    "alert_id",
    "transaction_id",
    "customer_id",
    "alert_type",
    "risk_score",
    "alert_status",
    "alert_description",
    "detected_time",
    "investigated_by",
    "investigation_notes",
    "resolved_time",
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    fail(
        "Missing required CSV columns:\n"
        + "\n".join(
            f" - {column}"
            for column in missing_columns
        ),
        cursor,
        conn
    )


print()
print("Required CSV Columns Validation Passed")


# ============================================================
# DATA TYPE CONVERSION
# ============================================================

df["alert_id"] = pd.to_numeric(
    df["alert_id"],
    errors="coerce"
)

df["transaction_id"] = pd.to_numeric(
    df["transaction_id"],
    errors="coerce"
)

df["customer_id"] = pd.to_numeric(
    df["customer_id"],
    errors="coerce"
)

df["risk_score"] = pd.to_numeric(
    df["risk_score"],
    errors="coerce"
)

df["detected_time"] = pd.to_datetime(
    df["detected_time"],
    errors="coerce"
)

df["resolved_time"] = pd.to_datetime(
    df["resolved_time"],
    errors="coerce"
)


# ============================================================
# REQUIRED FIELD VALIDATION
# ============================================================

print_header("REQUIRED FIELD VALIDATION")

required_data_columns = [
    "alert_id",
    "transaction_id",
    "customer_id",
    "alert_type",
    "detected_time",
]


null_counts = df[
    required_data_columns
].isnull().sum()


total_nulls = int(
    null_counts.sum()
)


print(
    "NULL Values in Required Columns :",
    total_nulls
)


if total_nulls > 0:

    print()

    print(
        null_counts[
            null_counts > 0
        ].to_string()
    )

    fail(
        "NULL values found in required fraud alert fields.",
        cursor,
        conn
    )


print(
    "No NULL values found in required columns."
)


# ============================================================
# DUPLICATE ALERT ID VALIDATION
# ============================================================

duplicate_alert_ids = int(
    df["alert_id"]
    .duplicated()
    .sum()
)


print()
print(
    "Duplicate Alert IDs :",
    duplicate_alert_ids
)


if duplicate_alert_ids != 0:

    fail(
        "Duplicate alert IDs found in CSV.",
        cursor,
        conn
    )


# ============================================================
# DUPLICATE TRANSACTION VALIDATION
# ============================================================

duplicate_transaction_ids = int(
    df["transaction_id"]
    .duplicated()
    .sum()
)


print(
    "Duplicate Transaction IDs :",
    duplicate_transaction_ids
)


# NOTE:
# Multiple fraud alerts can legitimately reference the same
# transaction, so duplicate transaction IDs are NOT treated
# as an error here.


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


if invalid_risk_scores != 0:

    fail(
        "Invalid risk scores found.",
        cursor,
        conn
    )


# ============================================================
# DATE VALIDATION
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


if invalid_resolved_dates != 0:

    fail(
        "Some resolved dates occur before detected dates.",
        cursor,
        conn
    )


# ============================================================
# TRANSACTION FOREIGN KEY VALIDATION
# ============================================================

print_header("FOREIGN KEY VALIDATION")


transaction_ids = (
    df["transaction_id"]
    .astype("int64")
    .tolist()
)


try:

    cursor.execute(
        """
        SELECT transaction_id
        FROM transactions
        WHERE transaction_id = ANY(%s);
        """,
        (transaction_ids,)
    )

    valid_transaction_ids = {
        int(row[0])
        for row in cursor.fetchall()
    }

except Exception as e:

    conn.rollback()

    fail(
        f"Transaction foreign key validation failed.\n\n{e}",
        cursor,
        conn
    )


invalid_transaction_ids = (
    set(transaction_ids)
    -
    valid_transaction_ids
)


print(
    "Invalid Transaction IDs :",
    len(invalid_transaction_ids)
)


if invalid_transaction_ids:

    fail(
        "Invalid transaction IDs found.",
        cursor,
        conn
    )


# ============================================================
# CUSTOMER FOREIGN KEY VALIDATION
# ============================================================

customer_ids = (
    df["customer_id"]
    .astype("int64")
    .tolist()
)


try:

    cursor.execute(
        """
        SELECT customer_id
        FROM customers
        WHERE customer_id = ANY(%s);
        """,
        (customer_ids,)
    )

    valid_customer_ids = {
        int(row[0])
        for row in cursor.fetchall()
    }

except Exception as e:

    conn.rollback()

    fail(
        f"Customer foreign key validation failed.\n\n{e}",
        cursor,
        conn
    )


invalid_customer_ids = (
    set(customer_ids)
    -
    valid_customer_ids
)


print(
    "Invalid Customer IDs :",
    len(invalid_customer_ids)
)


if invalid_customer_ids:

    fail(
        "Invalid customer IDs found.",
        cursor,
        conn
    )


print()
print("Foreign Key Validation Passed")


# ============================================================
# CHECK EXISTING ALERT IDS
# ============================================================

print_header("CHECKING EXISTING FRAUD ALERT IDS")


alert_ids = (
    df["alert_id"]
    .astype("int64")
    .tolist()
)


try:

    cursor.execute(
        """
        SELECT alert_id
        FROM fraud_alerts
        WHERE alert_id = ANY(%s);
        """,
        (alert_ids,)
    )

    existing_alert_ids = {
        int(row[0])
        for row in cursor.fetchall()
    }

except Exception as e:

    conn.rollback()

    fail(
        f"Unable to check existing alert IDs.\n\n{e}",
        cursor,
        conn
    )


print(
    "Alert IDs Already in Database :",
    len(existing_alert_ids)
)


if existing_alert_ids:

    print()
    print(
        "ERROR: Some fraud alert IDs already exist in database."
    )

    print(
        "The loader will NOT delete existing fraud alerts."
    )

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# PREPARE DATA FOR POSTGRESQL
# ============================================================

print_header("PREPARING FRAUD ALERT DATA")


insert_columns = [
    "alert_id",
    "transaction_id",
    "customer_id",
    "alert_type",
    "risk_score",
    "alert_status",
    "alert_description",
    "detected_time",
    "investigated_by",
    "investigation_notes",
    "resolved_time",
]


# ============================================================
# IMPORTANT:
# Convert Pandas NaN / NaT to Python None
# ============================================================

def convert_value(value):

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):

        if pd.isna(value):
            return None

        return value.to_pydatetime()

    return value


values = []


for _, row in df.iterrows():

    record = tuple(
        convert_value(row[column])
        for column in insert_columns
    )

    values.append(record)


print(
    f"Records Prepared : {len(values):,}"
)


# ============================================================
# DISPLAY NULL INFORMATION
# ============================================================

null_resolved_times = sum(
    1
    for record in values
    if record[-1] is None
)


null_investigators = sum(
    1
    for record in values
    if record[8] is None
)


null_notes = sum(
    1
    for record in values
    if record[9] is None
)


print()
print(
    "NULL resolved_time values :",
    null_resolved_times
)

print(
    "NULL investigated_by values :",
    null_investigators
)

print(
    "NULL investigation_notes values :",
    null_notes
)


# ============================================================
# CHECK ALERT_ID IDENTITY DEFINITION
# ============================================================

try:

    cursor.execute(
        """
        SELECT
            is_identity
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'fraud_alerts'
          AND column_name = 'alert_id';
        """
    )

    identity_result = cursor.fetchone()

except Exception as e:

    conn.rollback()

    fail(
        f"Unable to determine alert_id definition.\n\n{e}",
        cursor,
        conn
    )


if identity_result is None:

    fail(
        "fraud_alerts.alert_id column was not found.",
        cursor,
        conn
    )


is_identity = identity_result[0]


# ============================================================
# INSERT INTO POSTGRESQL
# ============================================================

print_header("LOADING FRAUD ALERTS INTO POSTGRESQL")


column_sql = ", ".join(
    insert_columns
)


if is_identity == "YES":

    insert_sql = f"""
        INSERT INTO fraud_alerts (
            {column_sql}
        )
        OVERRIDING SYSTEM VALUE
        VALUES %s
    """

else:

    insert_sql = f"""
        INSERT INTO fraud_alerts (
            {column_sql}
        )
        VALUES %s
    """


try:

    extras.execute_values(
        cursor,
        insert_sql,
        values,
        page_size=5000
    )

    print()
    print(
        "Fraud Alert Rows Inserted Successfully"
    )


    # ========================================================
    # COMMIT
    # ========================================================

    conn.commit()

    print(
        "Fraud Alert Data Committed Successfully"
    )


except Exception as e:

    conn.rollback()

    print()
    print("=" * 65)
    print("ERROR WHILE LOADING FRAUD ALERTS")
    print("=" * 65)

    print(e)

    print()
    print(
        "Transaction rolled back."
    )

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# POST-LOAD VALIDATION
# ============================================================

print_header("POST-LOAD VALIDATION")


try:

    # --------------------------------------------------------
    # Total Records
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM fraud_alerts;
        """
    )

    total_fraud_alerts = cursor.fetchone()[0]


    print(
        "Total Fraud Alerts in Database :",
        f"{total_fraud_alerts:,}"
    )


    # --------------------------------------------------------
    # Invalid Transaction References
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM fraud_alerts fa
        LEFT JOIN transactions t
            ON fa.transaction_id = t.transaction_id
        WHERE t.transaction_id IS NULL;
        """
    )

    invalid_transaction_references = (
        cursor.fetchone()[0]
    )


    print(
        "Invalid Transaction References :",
        invalid_transaction_references
    )


    # --------------------------------------------------------
    # Invalid Customer References
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM fraud_alerts fa
        LEFT JOIN customers c
            ON fa.customer_id = c.customer_id
        WHERE c.customer_id IS NULL;
        """
    )

    invalid_customer_references = (
        cursor.fetchone()[0]
    )


    print(
        "Invalid Customer References :",
        invalid_customer_references
    )


    # --------------------------------------------------------
    # Duplicate Alert IDs
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT alert_id
            FROM fraud_alerts
            GROUP BY alert_id
            HAVING COUNT(*) > 1
        ) duplicates;
        """
    )

    duplicate_alert_ids_db = (
        cursor.fetchone()[0]
    )


    print(
        "Duplicate Alert IDs :",
        duplicate_alert_ids_db
    )


    # --------------------------------------------------------
    # Required NULL Values
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM fraud_alerts
        WHERE alert_id IS NULL
           OR transaction_id IS NULL
           OR customer_id IS NULL
           OR alert_type IS NULL
           OR detected_time IS NULL;
        """
    )

    required_nulls_db = (
        cursor.fetchone()[0]
    )


    print(
        "NULL Required Values :",
        required_nulls_db
    )


    # --------------------------------------------------------
    # Compare CSV Count With Database
    # --------------------------------------------------------

    expected_count = len(df)


    print()
    print(
        "Expected CSV Records :",
        f"{expected_count:,}"
    )

    print(
        "Database Records :",
        f"{total_fraud_alerts:,}"
    )


    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    validation_passed = (
        total_fraud_alerts == expected_count
        and invalid_transaction_references == 0
        and invalid_customer_references == 0
        and duplicate_alert_ids_db == 0
        and required_nulls_db == 0
    )


    if validation_passed:

        print()
        print("=" * 65)
        print("FRAUD ALERT LOAD VALIDATION PASSED")
        print("=" * 65)

    else:

        print()
        print("=" * 65)
        print("FRAUD ALERT LOAD VALIDATION FAILED")
        print("=" * 65)

        cursor.close()
        conn.close()

        sys.exit(1)


except Exception as e:

    conn.rollback()

    print()
    print("=" * 65)
    print("ERROR DURING POST-LOAD VALIDATION")
    print("=" * 65)

    print(e)

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
conn.close()


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 65)
print("FRAUD ALERTS LOADED SUCCESSFULLY")
print("=" * 65)

print()
print("Fraud Alert Load Process Completed")

print("=" * 65)