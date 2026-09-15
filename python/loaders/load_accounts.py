import pandas as pd
import psycopg2


# ============================================================
# Project: Enterprise Banking Data Warehouse
# Module: Account Management
# Description: Loads accounts.csv into PostgreSQL
# ============================================================


# ============================================================
# 1. CONNECT TO POSTGRESQL
# ============================================================

conn = psycopg2.connect(
    host="localhost",
    database="enterprisebankingdw",
    user="postgres",
    password="1976",
    port="5432"
)

cursor = conn.cursor()

print("--------------------------------")
print("Database Connected Successfully")
print("--------------------------------")


# ============================================================
# 2. CHECK EXISTING ACCOUNTS
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM accounts
""")

existing_accounts = cursor.fetchone()[0]

print()
print("--------------------------------")
print("Existing Accounts :", existing_accounts)
print("--------------------------------")


# ============================================================
# 3. SAFETY CHECK
# ============================================================

if existing_accounts > 0:

    print()
    print("WARNING")
    print("--------------------------------")
    print("The accounts table already contains data.")
    print("No records were inserted.")
    print("--------------------------------")
    print()
    print("Existing Accounts :", existing_accounts)
    print()
    print("We must clean the existing account data")
    print("before loading the new 75,129 accounts.")
    print()

    cursor.close()
    conn.close()

    raise SystemExit


# ============================================================
# 4. READ ACCOUNTS CSV
# ============================================================

df = pd.read_csv(
    "data/raw/accounts.csv"
)


print()
print("--------------------------------")
print("Accounts CSV Loaded Successfully")
print("--------------------------------")
print()

print(df.head())

print()

print("Total Records :", len(df))


# ============================================================
# 5. CHECK FOR EMPTY CSV
# ============================================================

if df.empty:

    print()
    print("ERROR: Accounts CSV is empty.")

    cursor.close()
    conn.close()

    raise SystemExit


# ============================================================
# 6. REQUIRED COLUMNS
# ============================================================

required_columns = [

    "account_id",
    "account_number",
    "customer_id",
    "branch_id",
    "account_type",
    "account_status",
    "current_balance",
    "available_balance",
    "interest_rate",
    "opened_date",
    "closed_date",
    "currency"

]


# ============================================================
# 7. VALIDATE CSV COLUMNS
# ============================================================

missing_columns = [

    column
    for column in required_columns
    if column not in df.columns

]


if missing_columns:

    print()
    print("--------------------------------")
    print("ERROR: Missing CSV Columns")
    print("--------------------------------")
    print()

    print(missing_columns)

    cursor.close()
    conn.close()

    raise SystemExit


# ============================================================
# 8. INSERT QUERY
# ============================================================

insert_query = """

INSERT INTO accounts
(
    account_id,
    account_number,
    customer_id,
    branch_id,
    account_type,
    account_status,
    current_balance,
    available_balance,
    interest_rate,
    opened_date,
    closed_date,
    currency
)

OVERRIDING SYSTEM VALUE

VALUES
(
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
)

"""


# ============================================================
# 9. LOAD ACCOUNTS
# ============================================================

successful_rows = 0
failed_rows = 0


for index, row in df.iterrows():

    try:

        cursor.execute(
            insert_query,
            (

                int(row["account_id"]),

                row["account_number"],

                int(row["customer_id"]),

                int(row["branch_id"]),

                row["account_type"],

                row["account_status"],

                float(row["current_balance"]),

                float(row["available_balance"]),

                float(row["interest_rate"]),

                row["opened_date"],

                None
                if pd.isna(row["closed_date"])
                else row["closed_date"],

                row["currency"]

            )
        )

        successful_rows += 1


    except Exception as e:

        failed_rows += 1

        print()
        print("--------------------------------")
        print(
            f"Error loading row {index + 1}"
        )
        print("--------------------------------")

        print(e)

        conn.rollback()

        continue


# ============================================================
# 10. COMMIT TRANSACTION
# ============================================================

conn.commit()


# ============================================================
# 11. VERIFY DATABASE COUNT
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM accounts
""")

database_count = cursor.fetchone()[0]


# ============================================================
# 12. CLOSE DATABASE CONNECTION
# ============================================================

cursor.close()

conn.close()


# ============================================================
# 13. FINAL LOAD SUMMARY
# ============================================================

print()
print("================================")
print("ACCOUNT LOAD COMPLETED")
print("================================")
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

print()


# ============================================================
# 14. FINAL VALIDATION
# ============================================================

if (
    successful_rows == len(df)
    and failed_rows == 0
    and database_count == len(df)
):

    print("--------------------------------")
    print("Accounts Loaded Successfully")
    print("--------------------------------")

else:

    print("--------------------------------")
    print("ACCOUNT LOAD VALIDATION FAILED")
    print("--------------------------------")

print()