import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from getpass import getpass


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

CSV_FILE = "data/raw/transactions.csv"
BATCH_SIZE = 5000

DB_HOST = "localhost"
DB_NAME = "enterprisebankingdw"
DB_USER = "postgres"
DB_PORT = "5432"


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

print()
print("============================================================")
print("CONNECTING TO POSTGRESQL")
print("============================================================")

DB_PASSWORD = os.getenv("PGPASSWORD")

if not DB_PASSWORD:
    DB_PASSWORD = getpass("Enter PostgreSQL password: ")


conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

cursor = conn.cursor()

print()
print("Database Connected Successfully")


# ============================================================
# CHECK TRANSACTIONS TABLE
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM transactions
    """
)

existing_transactions = cursor.fetchone()[0]

print()
print("Existing Transactions :", existing_transactions)


# ============================================================
# READ TRANSACTIONS CSV
# ============================================================

print()
print("============================================================")
print("READING TRANSACTIONS CSV")
print("============================================================")

if not os.path.exists(CSV_FILE):

    print()
    print("ERROR: Transactions CSV file was not found.")
    print("Expected File :", CSV_FILE)

    cursor.close()
    conn.close()
    raise SystemExit


df = pd.read_csv(CSV_FILE)


if df.empty:

    print()
    print("ERROR: Transaction CSV is empty.")

    cursor.close()
    conn.close()
    raise SystemExit


print()
print("Transactions CSV Loaded Successfully")

print()
print("Total Records :", len(df))


# ============================================================
# DISPLAY SAMPLE DATA
# ============================================================

print()
print("============================================================")
print("SAMPLE TRANSACTIONS")
print("============================================================")

print(
    df.head(5).to_string(index=False)
)


# ============================================================
# REQUIRED CSV COLUMNS
# ============================================================

required_columns = [

    "transaction_id",
    "transaction_number",
    "account_id",
    "customer_id",
    "branch_id",
    "transaction_date",
    "transaction_type",
    "transaction_category",
    "amount",
    "currency",
    "transaction_status",
    "channel",
    "description",
    "balance_after_transaction"

]


missing_columns = [

    column
    for column in required_columns
    if column not in df.columns

]


print()
print("============================================================")
print("CSV COLUMN VALIDATION")
print("============================================================")

print()
print("Missing Transaction Columns :", missing_columns)


if missing_columns:

    print()
    print("ERROR: Required columns are missing from transactions.csv.")

    cursor.close()
    conn.close()
    raise SystemExit


print()
print("Required CSV Columns Validation Passed")


# ============================================================
# CONVERT DATA TYPES
# ============================================================

df["transaction_id"] = pd.to_numeric(
    df["transaction_id"],
    errors="coerce"
)

df["account_id"] = pd.to_numeric(
    df["account_id"],
    errors="coerce"
)

df["customer_id"] = pd.to_numeric(
    df["customer_id"],
    errors="coerce"
)

df["branch_id"] = pd.to_numeric(
    df["branch_id"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)

df["balance_after_transaction"] = pd.to_numeric(
    df["balance_after_transaction"],
    errors="coerce"
)

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce"
)


# ============================================================
# NULL VALUE VALIDATION
# ============================================================

print()
print("============================================================")
print("NULL VALUE VALIDATION")
print("============================================================")


null_counts = df[
    required_columns
].isnull().sum()


total_nulls = null_counts.sum()


if total_nulls > 0:

    print()
    print("NULL values found:")

    print(
        null_counts[
            null_counts > 0
        ]
    )

    cursor.close()
    conn.close()
    raise SystemExit


print()
print("No NULL values found in required columns.")


# ============================================================
# DUPLICATE TRANSACTION ID VALIDATION
# ============================================================

duplicate_ids = (
    df["transaction_id"]
    .duplicated()
    .sum()
)


print()
print("Duplicate Transaction IDs :", duplicate_ids)


if duplicate_ids > 0:

    print()
    print("ERROR: Duplicate transaction IDs found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ============================================================
# DUPLICATE TRANSACTION NUMBER VALIDATION
# ============================================================

duplicate_numbers = (
    df["transaction_number"]
    .duplicated()
    .sum()
)


print()
print(
    "Duplicate Transaction Numbers :",
    duplicate_numbers
)


if duplicate_numbers > 0:

    print()
    print("ERROR: Duplicate transaction numbers found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ============================================================
# TRANSACTION ID VALIDATION
# ============================================================

invalid_transaction_ids = (
    df["transaction_id"] <= 0
).sum()


print()
print(
    "Invalid Transaction IDs :",
    invalid_transaction_ids
)


if invalid_transaction_ids > 0:

    print()
    print("ERROR: Invalid transaction IDs found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ============================================================
# TRANSACTION AMOUNT VALIDATION
# ============================================================

invalid_amounts = (
    df["amount"] <= 0
).sum()


print()
print(
    "Invalid Transaction Amounts :",
    invalid_amounts
)


if invalid_amounts > 0:

    print()
    print("ERROR: Invalid transaction amounts found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ============================================================
# BALANCE VALIDATION
# ============================================================

invalid_balances = (
    df["balance_after_transaction"] < 0
).sum()


print()
print(
    "Negative Balance Records :",
    invalid_balances
)


if invalid_balances > 0:

    print()
    print("ERROR: Negative account balances found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ============================================================
# TRANSACTION DATE VALIDATION
# ============================================================

future_dates = (
    df["transaction_date"] > pd.Timestamp.now()
).sum()


print()
print(
    "Future Transaction Dates :",
    future_dates
)


if future_dates > 0:

    print()
    print("ERROR: Future transaction dates found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ============================================================
# FOREIGN KEY VALIDATION
# ============================================================

print()
print("============================================================")
print("FOREIGN KEY VALIDATION")
print("============================================================")


# ------------------------------------------------------------
# ACCOUNTS
# ------------------------------------------------------------

cursor.execute(
    """
    SELECT account_id
    FROM accounts
    """
)

valid_account_ids = {
    row[0]
    for row in cursor.fetchall()
}


invalid_account_ids = (
    ~df["account_id"]
    .isin(valid_account_ids)
).sum()


print()
print(
    "Invalid Account IDs :",
    invalid_account_ids
)


if invalid_account_ids > 0:

    print()
    print("ERROR: Invalid account IDs found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ------------------------------------------------------------
# CUSTOMERS
# ------------------------------------------------------------

cursor.execute(
    """
    SELECT customer_id
    FROM customers
    """
)

valid_customer_ids = {
    row[0]
    for row in cursor.fetchall()
}


invalid_customer_ids = (
    ~df["customer_id"]
    .isin(valid_customer_ids)
).sum()


print()
print(
    "Invalid Customer IDs :",
    invalid_customer_ids
)


if invalid_customer_ids > 0:

    print()
    print("ERROR: Invalid customer IDs found.")

    cursor.close()
    conn.close()
    raise SystemExit


# ------------------------------------------------------------
# BRANCHES
# ------------------------------------------------------------

cursor.execute(
    """
    SELECT branch_id
    FROM branches
    """
)

valid_branch_ids = {
    row[0]
    for row in cursor.fetchall()
}


invalid_branch_ids = (
    ~df["branch_id"]
    .isin(valid_branch_ids)
).sum()


print()
print(
    "Invalid Branch IDs :",
    invalid_branch_ids
)


if invalid_branch_ids > 0:

    print()
    print("ERROR: Invalid branch IDs found.")

    cursor.close()
    conn.close()
    raise SystemExit


print()
print("Foreign Key Validation Passed")


# ============================================================
# GET ACTUAL TRANSACTIONS TABLE COLUMNS
# ============================================================

print()
print("============================================================")
print("CHECKING TRANSACTIONS TABLE STRUCTURE")
print("============================================================")


cursor.execute(
    """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'transactions'
    ORDER BY ordinal_position
    """
)

database_columns = {
    row[0]
    for row in cursor.fetchall()
}


print()
print("Transactions Table Columns:")

for column in sorted(database_columns):
    print(" -", column)


# ============================================================
# CHECK IMPORTANT DATABASE COLUMNS
# ============================================================

expected_database_columns = [

    "transaction_id",
    "account_id",
    "transaction_type",
    "transaction_amount",
    "transaction_status",
    "transaction_channel",
    "transaction_date",
    "description"

]


missing_database_columns = [

    column
    for column in expected_database_columns
    if column not in database_columns

]


if missing_database_columns:

    print()
    print(
        "ERROR: Required database columns are missing:"
    )

    for column in missing_database_columns:
        print(" -", column)

    cursor.close()
    conn.close()
    raise SystemExit


print()
print("Database Structure Validation Passed")


# ============================================================
# CHECK EXISTING TRANSACTION IDS
# ============================================================

print()
print("============================================================")
print("CHECKING EXISTING TRANSACTION IDs")
print("============================================================")


existing_ids = set()


if existing_transactions > 0:

    cursor.execute(
        """
        SELECT transaction_id
        FROM transactions
        """
    )

    existing_ids = {
        row[0]
        for row in cursor.fetchall()
    }


duplicate_database_ids = (
    df["transaction_id"]
    .isin(existing_ids)
).sum()


print()
print(
    "Transaction IDs Already in Database :",
    duplicate_database_ids
)


if duplicate_database_ids > 0:

    print()
    print(
        "ERROR: Some transaction IDs already exist in database."
    )

    print()
    print(
        "The loader will NOT delete existing transactions."
    )

    cursor.close()
    conn.close()
    raise SystemExit


# ============================================================
# CHECK EXISTING TRANSACTION NUMBERS
# ============================================================

if "transaction_number" in database_columns:

    cursor.execute(
        """
        SELECT transaction_number
        FROM transactions
        WHERE transaction_number IS NOT NULL
        """
    )

    existing_numbers = {
        row[0]
        for row in cursor.fetchall()
    }

    duplicate_database_numbers = (
        df["transaction_number"]
        .isin(existing_numbers)
    ).sum()

    print()
    print(
        "Transaction Numbers Already in Database :",
        duplicate_database_numbers
    )

    if duplicate_database_numbers > 0:

        print()
        print(
            "ERROR: Some transaction numbers already exist."
        )

        cursor.close()
        conn.close()
        raise SystemExit


# ============================================================
# BUILD DATABASE INSERT COLUMNS
# ============================================================

print()
print("============================================================")
print("PREPARING TRANSACTION INSERT")
print("============================================================")


insert_columns = []
record_builders = []


# ------------------------------------------------------------
# TRANSACTION ID
# ------------------------------------------------------------

insert_columns.append("transaction_id")

record_builders.append(
    lambda row: int(row["transaction_id"])
)


# ------------------------------------------------------------
# TRANSACTION REFERENCE
# ------------------------------------------------------------

if "transaction_reference" in database_columns:

    insert_columns.append("transaction_reference")

    record_builders.append(
        lambda row: row["transaction_number"]
    )


# ------------------------------------------------------------
# TRANSACTION NUMBER
# ------------------------------------------------------------

if "transaction_number" in database_columns:

    insert_columns.append("transaction_number")

    record_builders.append(
        lambda row: row["transaction_number"]
    )


# ------------------------------------------------------------
# ACCOUNT ID
# ------------------------------------------------------------

insert_columns.append("account_id")

record_builders.append(
    lambda row: int(row["account_id"])
)


# ------------------------------------------------------------
# TRANSACTION TYPE
# ------------------------------------------------------------

insert_columns.append("transaction_type")

record_builders.append(
    lambda row: row["transaction_type"]
)


# ------------------------------------------------------------
# TRANSACTION AMOUNT
# ------------------------------------------------------------

insert_columns.append("transaction_amount")

record_builders.append(
    lambda row: float(row["amount"])
)


# ------------------------------------------------------------
# TRANSACTION STATUS
# ------------------------------------------------------------

insert_columns.append("transaction_status")

record_builders.append(
    lambda row: row["transaction_status"]
)


# ------------------------------------------------------------
# TRANSACTION CHANNEL
# ------------------------------------------------------------

insert_columns.append("transaction_channel")

record_builders.append(
    lambda row: row["channel"]
)


# ------------------------------------------------------------
# TRANSACTION DATE
# ------------------------------------------------------------

insert_columns.append("transaction_date")

record_builders.append(
    lambda row: row["transaction_date"].to_pydatetime()
)


# ------------------------------------------------------------
# DESCRIPTION
# ------------------------------------------------------------

insert_columns.append("description")

record_builders.append(
    lambda row: row["description"]
)


# ------------------------------------------------------------
# BALANCE AFTER TRANSACTION
# ------------------------------------------------------------

if "balance_after_transaction" in database_columns:

    insert_columns.append(
        "balance_after_transaction"
    )

    record_builders.append(
        lambda row: float(
            row["balance_after_transaction"]
        )
    )

    print()
    print(
        "balance_after_transaction will be loaded."
    )

else:

    print()
    print(
        "WARNING: balance_after_transaction does not exist "
        "in PostgreSQL transactions table."
    )

    print(
        "The CSV contains the column, but PostgreSQL does not."
    )


# ============================================================
# CREATE INSERT SQL
# ============================================================

column_sql = ", ".join(
    insert_columns
)

value_sql = ", ".join(
    ["%s"] * len(insert_columns)
)


insert_query = f"""
INSERT INTO transactions
(
    {column_sql}
)
OVERRIDING SYSTEM VALUE
VALUES
(
    {value_sql}
)
"""


print()
print("Insert Columns:")

for column in insert_columns:
    print(" -", column)


# ============================================================
# PREPARE RECORDS
# ============================================================

print()
print("============================================================")
print("PREPARING TRANSACTION DATA")
print("============================================================")


records = []


for _, row in df.iterrows():

    record = tuple(
        builder(row)
        for builder in record_builders
    )

    records.append(record)


print()
print("Records Prepared :", len(records))


# ============================================================
# LOAD TRANSACTIONS
# ============================================================

print()
print("============================================================")
print("LOADING TRANSACTIONS INTO POSTGRESQL")
print("============================================================")


successful_rows = 0
failed_rows = 0


try:

    execute_batch(
        cursor,
        insert_query,
        records,
        page_size=BATCH_SIZE
    )

    successful_rows = len(records)

    conn.commit()

    print()
    print("Transaction Data Committed Successfully")


except Exception as e:

    failed_rows = len(records)

    print()
    print("============================================================")
    print("ERROR WHILE LOADING TRANSACTIONS")
    print("============================================================")

    print()
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    raise SystemExit


# ============================================================
# SYNCHRONIZE TRANSACTION IDENTITY / SEQUENCE
# ============================================================

print()
print("============================================================")
print("SYNCHRONIZING TRANSACTION ID SEQUENCE")
print("============================================================")


try:

    cursor.execute(
        """
        SELECT pg_get_serial_sequence(
            'transactions',
            'transaction_id'
        )
        """
    )

    sequence_name = cursor.fetchone()[0]


    if sequence_name:

        cursor.execute(
            f"""
            SELECT setval(
                %s,
                COALESCE(
                    (
                        SELECT MAX(transaction_id)
                        FROM transactions
                    ),
                    1
                ),
                true
            )
            """,
            (sequence_name,)
        )

        conn.commit()

        print()
        print(
            "Transaction Identity Sequence Synchronized"
        )

    else:

        print()
        print(
            "No transaction identity sequence detected."
        )


except Exception as e:

    conn.rollback()

    print()
    print(
        "Sequence synchronization skipped:"
    )

    print(e)


# ============================================================
# DATABASE COUNT
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM transactions
    """
)

database_count = cursor.fetchone()[0]


# ============================================================
# FINAL LOAD VALIDATION
# ============================================================

print()
print("============================================================")
print("FINAL LOAD VALIDATION")
print("============================================================")


print()
print(
    "CSV Records       :",
    len(df)
)

print(
    "Successful Rows   :",
    successful_rows
)

print(
    "Failed Rows       :",
    failed_rows
)

print(
    "Database Records  :",
    database_count
)


# ============================================================
# VERIFY BALANCE DATA
# ============================================================

if "balance_after_transaction" in database_columns:

    cursor.execute(
        """
        SELECT
            COUNT(*)
        FROM transactions
        WHERE balance_after_transaction IS NULL
        """
    )

    null_balance_count = cursor.fetchone()[0]

    print()
    print(
        "NULL Balance Records :",
        null_balance_count
    )

else:

    null_balance_count = None


# ============================================================
# VERIFY SAMPLE RECORDS
# ============================================================

print()
print("============================================================")
print("DATABASE SAMPLE")
print("============================================================")


sample_columns = [

    "transaction_id"

]


if "transaction_reference" in database_columns:
    sample_columns.append("transaction_reference")


if "transaction_number" in database_columns:
    sample_columns.append("transaction_number")


sample_columns.extend(
    [
        "account_id",
        "transaction_type",
        "transaction_amount",
        "transaction_status",
        "transaction_channel",
        "transaction_date",
        "description"
    ]
)


if "balance_after_transaction" in database_columns:

    sample_columns.append(
        "balance_after_transaction"
    )


sample_column_sql = ", ".join(
    sample_columns
)


cursor.execute(
    f"""
    SELECT
        {sample_column_sql}
    FROM transactions
    ORDER BY transaction_id
    LIMIT 10
    """
)


sample_rows = cursor.fetchall()


print()


for row in sample_rows:

    print(row)


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
conn.close()


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("============================================================")


load_successful = (

    successful_rows == len(df)
    and failed_rows == 0
)


if "balance_after_transaction" in database_columns:

    load_successful = (
        load_successful
        and null_balance_count == 0
    )


if load_successful:

    print()
    print("TRANSACTIONS LOADED SUCCESSFULLY")

else:

    print()
    print("TRANSACTION LOAD VALIDATION FAILED")


print()
print("============================================================")

print()
print(
    "Transaction Load Process Completed"
)

print()