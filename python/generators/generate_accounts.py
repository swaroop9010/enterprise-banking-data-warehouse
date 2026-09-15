import pandas as pd
import psycopg2
import random
from datetime import timedelta, date


# ============================================================
# Project: Enterprise Banking Data Warehouse
# Module: Account Management
# Description: Generates realistic banking account data
#              using customers and branches from PostgreSQL
# ============================================================


# ============================================================
# 1. DATABASE CONNECTION
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
# 2. READ CUSTOMERS FROM CSV
# ============================================================

customers = pd.read_csv(
    "data/raw/customers.csv"
)

print()
print("--------------------------------")
print("Customers CSV Loaded Successfully")
print("--------------------------------")
print()

print("Total Customers :", len(customers))


# ============================================================
# 3. VALIDATE CUSTOMER DATA
# ============================================================

required_customer_columns = [
    "customer_id",
    "customer_since",
    "branch_id"
]

missing_columns = [
    column
    for column in required_customer_columns
    if column not in customers.columns
]

if missing_columns:

    print()
    print("ERROR: Missing customer columns:")
    print(missing_columns)

    cursor.close()
    conn.close()

    raise SystemExit


# ============================================================
# 4. READ BRANCH IDs FROM POSTGRESQL
# ============================================================

cursor.execute("""
    SELECT branch_id
    FROM branches
    ORDER BY branch_id
""")

branch_ids = [
    row[0]
    for row in cursor.fetchall()
]


print()
print("--------------------------------")
print("Branches Found :", len(branch_ids))
print("--------------------------------")


# ============================================================
# 5. VALIDATE BRANCH DATA
# ============================================================

if len(branch_ids) == 0:

    print()
    print("ERROR: No branches found in PostgreSQL.")

    cursor.close()
    conn.close()

    raise SystemExit


# ============================================================
# 6. MASTER ACCOUNT TYPES
# ============================================================

account_types = [
    "Checking",
    "Savings",
    "Money Market",
    "Certificate of Deposit"
]


# ============================================================
# 7. ACCOUNT STATUS
# ============================================================

account_statuses = [
    "Active",
    "Inactive",
    "Frozen",
    "Closed"
]


# ============================================================
# 8. CURRENCY
# ============================================================

currencies = [
    "USD"
]


# ============================================================
# 9. BALANCE RANGES
# ============================================================

balance_ranges = {

    "Checking": (
        0,
        75000
    ),

    "Savings": (
        100,
        150000
    ),

    "Money Market": (
        10000,
        1000000
    ),

    "Certificate of Deposit": (
        25000,
        500000
    )
}


# ============================================================
# 10. INTEREST RATES
# ============================================================

interest_rates = {

    "Checking": 0.10,

    "Savings": 2.25,

    "Money Market": 3.25,

    "Certificate of Deposit": 4.75
}


# ============================================================
# 11. ACCOUNT COLLECTION
# ============================================================

accounts = []


# ============================================================
# 12. ACCOUNT ID COUNTERS
# ============================================================

account_id = 1

account_number = 1


# ============================================================
# 13. GENERATE ACCOUNTS
# ============================================================

for index, customer in customers.iterrows():

    # --------------------------------------------------------
    # Determine number of accounts for each customer
    # --------------------------------------------------------

    number_of_accounts = random.choices(
        [1, 2, 3],
        weights=[60, 30, 10]
    )[0]


    # --------------------------------------------------------
    # Convert customer_since to a real Python date
    # --------------------------------------------------------

    customer_since = pd.to_datetime(
        customer["customer_since"]
    ).date()


    # --------------------------------------------------------
    # Generate accounts for customer
    # --------------------------------------------------------

    for i in range(number_of_accounts):

        # ----------------------------------------------------
        # Account Type
        # ----------------------------------------------------

        selected_account_type = random.choice(
            account_types
        )


        # ----------------------------------------------------
        # Account Status
        # ----------------------------------------------------

        selected_status = random.choices(
            account_statuses,
            weights=[75, 10, 5, 10]
        )[0]


        # ----------------------------------------------------
        # Generate Opening Date
        #
        # The opening date must be:
        #
        # customer_since <= opened_date <= today
        # ----------------------------------------------------

        days_since_customer = (
            date.today() - customer_since
        ).days


        if days_since_customer < 0:

            days_since_customer = 0


        random_days = random.randint(
            0,
            days_since_customer
        )


        opened_date = (
            customer_since +
            timedelta(days=random_days)
        )


        # ----------------------------------------------------
        # Generate Balance
        # ----------------------------------------------------

        minimum_balance, maximum_balance = balance_ranges[
            selected_account_type
        ]


        current_balance = round(
            random.uniform(
                minimum_balance,
                maximum_balance
            ),
            2
        )


        # ----------------------------------------------------
        # Available Balance
        #
        # Keep available balance <= current balance
        # ----------------------------------------------------

        available_balance = round(
            current_balance *
            random.uniform(0.90, 1.00),
            2
        )


        # ----------------------------------------------------
        # Interest Rate
        # ----------------------------------------------------

        interest_rate = interest_rates[
            selected_account_type
        ]


        # ----------------------------------------------------
        # Closed Date
        # ----------------------------------------------------

        closed_date = None


        if selected_status == "Closed":

            days_open = (
                date.today() - opened_date
            ).days


            if days_open > 0:

                closed_days = random.randint(
                    0,
                    days_open
                )

                closed_date = (
                    opened_date +
                    timedelta(days=closed_days)
                )


        # ----------------------------------------------------
        # Create Account Record
        # ----------------------------------------------------

        account = {

            "account_id": account_id,

            "account_number":
                f"ACC{account_number:08d}",

            "customer_id":
                int(customer["customer_id"]),

            "branch_id":
                int(customer["branch_id"]),

            "account_type":
                selected_account_type,

            "account_status":
                selected_status,

            "current_balance":
                current_balance,

            "available_balance":
                available_balance,

            "interest_rate":
                interest_rate,

            "opened_date":
                opened_date,

            "closed_date":
                closed_date,

            "currency":
                "USD"
        }


        # ----------------------------------------------------
        # Add Account to Collection
        # ----------------------------------------------------

        accounts.append(account)


        # ----------------------------------------------------
        # Increment IDs
        # ----------------------------------------------------

        account_id += 1

        account_number += 1


# ============================================================
# 14. CLOSE DATABASE CONNECTION
# ============================================================

cursor.close()

conn.close()


# ============================================================
# 15. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    accounts
)


# ============================================================
# 16. DISPLAY SAMPLE DATA
# ============================================================

print()
print("--------------------------------")
print("Accounts Generated Successfully")
print("--------------------------------")
print()

print(df.head(10))

print()


# ============================================================
# 17. DISPLAY ACCOUNT COUNT
# ============================================================

print("--------------------------------")
print("Total Accounts :", len(df))
print("--------------------------------")


# ============================================================
# 18. DISPLAY ACCOUNT TYPES
# ============================================================

print()
print("Account Type Distribution")
print("--------------------------------")

print(
    df["account_type"].value_counts()
)


# ============================================================
# 19. DISPLAY ACCOUNT STATUS
# ============================================================

print()
print("Account Status Distribution")
print("--------------------------------")

print(
    df["account_status"].value_counts()
)


# ============================================================
# 20. VALIDATE CUSTOMER IDs
# ============================================================

invalid_customer_ids = (
    ~df["customer_id"].isin(
        customers["customer_id"]
    )
).sum()


print()
print("--------------------------------")
print(
    "Invalid Customer IDs :",
    invalid_customer_ids
)
print("--------------------------------")


# ============================================================
# 21. VALIDATE BRANCH IDs
# ============================================================

invalid_branch_ids = (
    ~df["branch_id"].isin(
        branch_ids
    )
).sum()


print()
print("--------------------------------")
print(
    "Invalid Branch IDs :",
    invalid_branch_ids
)
print("--------------------------------")


# ============================================================
# 22. VALIDATE ACCOUNT DATES
# ============================================================

invalid_dates = (
    df["opened_date"] >
    date.today()
).sum()


print()
print("--------------------------------")
print(
    "Invalid Opening Dates :",
    invalid_dates
)
print("--------------------------------")


# ============================================================
# 23. VALIDATE CLOSED DATES
# ============================================================

invalid_closed_dates = 0


for index, row in df.iterrows():

    if pd.notna(row["closed_date"]):

        if row["closed_date"] < row["opened_date"]:

            invalid_closed_dates += 1


print()
print("--------------------------------")
print(
    "Invalid Closed Dates :",
    invalid_closed_dates
)
print("--------------------------------")


# ============================================================
# 24. SAVE ACCOUNTS CSV
# ============================================================

df.to_csv(
    "data/raw/accounts.csv",
    index=False
)


# ============================================================
# 25. FINAL SUCCESS MESSAGE
# ============================================================

print()
print("================================")
print("Accounts CSV Generated Successfully")
print("================================")
print()

print(
    "File : data/raw/accounts.csv"
)

print(
    "Rows :",
    len(df)
)

print()
print("Account Generation Completed Successfully")
print("================================")