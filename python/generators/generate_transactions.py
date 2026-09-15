import os
import pandas as pd
import random
from datetime import datetime, timedelta


# ============================================================
# Project: Enterprise Banking Data Warehouse
# Module: Transaction Management
# Description: Generates realistic banking transaction data
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_OF_TRANSACTIONS = 500000

INPUT_FILE = "data/raw/accounts.csv"
OUTPUT_FILE = "data/raw/transactions.csv"


# ============================================================
# READ ACCOUNTS
# ============================================================

print()
print("============================================================")
print("READING ACCOUNTS DATA")
print("============================================================")

accounts = pd.read_csv(INPUT_FILE)


if accounts.empty:

    print()
    print("Accounts CSV is empty.")
    raise SystemExit(1)


print()
print("Accounts Loaded Successfully")
print("Total Accounts :", len(accounts))


# ============================================================
# REQUIRED ACCOUNT COLUMNS
# ============================================================

required_account_columns = [
    "account_id",
    "customer_id",
    "branch_id",
    "account_type",
    "account_status",
    "opened_date"
]


missing_columns = [
    column
    for column in required_account_columns
    if column not in accounts.columns
]


if missing_columns:

    print()
    print("Missing Columns :", missing_columns)
    raise SystemExit(1)


print()
print("Required Account Columns Validation Passed")


# ============================================================
# CONVERT OPENED DATE
# ============================================================

accounts["opened_date"] = pd.to_datetime(
    accounts["opened_date"],
    errors="coerce"
)


# ============================================================
# REMOVE INVALID ACCOUNTS
# ============================================================

accounts = accounts.dropna(
    subset=[
        "account_id",
        "customer_id",
        "branch_id",
        "opened_date"
    ]
)


if accounts.empty:

    print()
    print("No valid accounts available.")
    raise SystemExit(1)


print()
print("Valid Accounts :", len(accounts))


# ============================================================
# REMOVE DUPLICATE ACCOUNT IDs
# ============================================================

duplicate_account_ids = (
    accounts["account_id"]
    .duplicated()
    .sum()
)


print()
print(
    "Duplicate Account IDs :",
    duplicate_account_ids
)


if duplicate_account_ids > 0:

    print()
    print("Duplicate account IDs found.")
    raise SystemExit(1)


# ============================================================
# TRANSACTION MASTER DATA
# ============================================================

transaction_types = [
    "Deposit",
    "Withdrawal",
    "Transfer",
    "Payment",
    "Fee",
    "Interest",
    "Refund"
]


transaction_type_weights = [
    25,
    20,
    20,
    15,
    8,
    5,
    7
]


transaction_categories = {

    "Deposit": [
        "Cash Deposit",
        "Check Deposit",
        "Direct Deposit",
        "Salary Deposit"
    ],

    "Withdrawal": [
        "ATM Withdrawal",
        "Cash Withdrawal"
    ],

    "Transfer": [
        "Internal Transfer",
        "External Transfer",
        "Wire Transfer"
    ],

    "Payment": [
        "Bill Payment",
        "Card Payment",
        "Online Payment"
    ],

    "Fee": [
        "Maintenance Fee",
        "ATM Fee",
        "Transfer Fee",
        "Overdraft Fee"
    ],

    "Interest": [
        "Interest Credit"
    ],

    "Refund": [
        "Payment Refund",
        "Card Refund"
    ]
}


transaction_statuses = [
    "Completed",
    "Pending",
    "Failed",
    "Reversed"
]


transaction_status_weights = [
    92,
    4,
    2,
    2
]


channels = [
    "Online Banking",
    "Mobile Banking",
    "ATM",
    "Branch",
    "POS",
    "ACH",
    "Wire"
]


channel_weights = [
    25,
    25,
    15,
    10,
    10,
    10,
    5
]


currency = "USD"


# ============================================================
# TRANSACTION AMOUNT RANGES
# ============================================================

amount_ranges = {

    "Deposit": (100, 25000),

    "Withdrawal": (20, 10000),

    "Transfer": (50, 50000),

    "Payment": (10, 10000),

    "Fee": (5, 500),

    "Interest": (1, 1000),

    "Refund": (10, 10000)
}


# ============================================================
# TRANSACTION DESCRIPTIONS
# ============================================================

descriptions = {

    "Deposit":
        "Customer deposit",

    "Withdrawal":
        "Customer withdrawal",

    "Transfer":
        "Funds transfer",

    "Payment":
        "Customer payment",

    "Fee":
        "Bank service fee",

    "Interest":
        "Interest credit",

    "Refund":
        "Customer refund"
}


# ============================================================
# PREPARE ACCOUNT RECORDS
# ============================================================

account_records = accounts.to_dict(
    orient="records"
)


# ============================================================
# INITIAL ACCOUNT BALANCES
# ============================================================

account_balances = {

    int(account["account_id"]):
        round(
            random.uniform(
                1000,
                50000
            ),
            2
        )

    for account in account_records
}


# ============================================================
# GENERATE TRANSACTIONS
# ============================================================

transactions = []


print()
print("============================================================")
print("GENERATING TRANSACTIONS")
print("============================================================")


for transaction_id in range(
    1,
    NUMBER_OF_TRANSACTIONS + 1
):

    # --------------------------------------------------------
    # SELECT ACCOUNT
    # --------------------------------------------------------

    account = random.choice(
        account_records
    )


    account_id = int(
        account["account_id"]
    )


    customer_id = int(
        account["customer_id"]
    )


    branch_id = int(
        account["branch_id"]
    )


    opened_date = account["opened_date"]


    # --------------------------------------------------------
    # TRANSACTION DATE
    # --------------------------------------------------------

    opened_datetime = opened_date.to_pydatetime()

    current_datetime = datetime.now()


    # Prevent future account opening dates
    if opened_datetime > current_datetime:

        opened_datetime = current_datetime


    date_difference = (
        current_datetime -
        opened_datetime
    ).days


    if date_difference > 0:

        random_days = random.randint(
            0,
            date_difference
        )

    else:

        random_days = 0


    transaction_datetime = (
        opened_datetime +
        timedelta(
            days=random_days
        )
    )


    # --------------------------------------------------------
    # TRANSACTION TYPE
    # --------------------------------------------------------

    transaction_type = random.choices(
        transaction_types,
        weights=transaction_type_weights,
        k=1
    )[0]


    # --------------------------------------------------------
    # TRANSACTION CATEGORY
    # --------------------------------------------------------

    transaction_category = random.choice(
        transaction_categories[
            transaction_type
        ]
    )


    # --------------------------------------------------------
    # TRANSACTION AMOUNT
    # --------------------------------------------------------

    minimum_amount, maximum_amount = (
        amount_ranges[
            transaction_type
        ]
    )


    amount = round(
        random.uniform(
            minimum_amount,
            maximum_amount
        ),
        2
    )


    # --------------------------------------------------------
    # TRANSACTION STATUS
    # --------------------------------------------------------

    transaction_status = random.choices(
        transaction_statuses,
        weights=transaction_status_weights,
        k=1
    )[0]


    # --------------------------------------------------------
    # CHECK AVAILABLE BALANCE
    # --------------------------------------------------------

    previous_balance = account_balances[
        account_id
    ]


    debit_transaction_types = [
        "Withdrawal",
        "Transfer",
        "Payment",
        "Fee"
    ]


    # --------------------------------------------------------
    # PREVENT UNREALISTIC NEGATIVE BALANCE
    # --------------------------------------------------------

    if (
        transaction_status == "Completed"
        and transaction_type in debit_transaction_types
        and amount > previous_balance
    ):

        transaction_status = "Failed"


    # --------------------------------------------------------
    # CALCULATE BALANCE
    # --------------------------------------------------------

    balance_after_transaction = previous_balance


    if transaction_status == "Completed":

        if transaction_type in [
            "Deposit",
            "Interest",
            "Refund"
        ]:

            balance_after_transaction += amount


        elif transaction_type in debit_transaction_types:

            balance_after_transaction -= amount


    balance_after_transaction = round(
        balance_after_transaction,
        2
    )


    # --------------------------------------------------------
    # UPDATE ACCOUNT BALANCE
    # --------------------------------------------------------

    account_balances[account_id] = (
        balance_after_transaction
    )


    # --------------------------------------------------------
    # CHANNEL
    # --------------------------------------------------------

    channel = random.choices(
        channels,
        weights=channel_weights,
        k=1
    )[0]


    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = descriptions[
        transaction_type
    ]


    # --------------------------------------------------------
    # TRANSACTION NUMBER
    # --------------------------------------------------------

    transaction_number = (
        f"TXN{transaction_id:09d}"
    )


    # --------------------------------------------------------
    # CREATE TRANSACTION
    # --------------------------------------------------------

    transaction = {

        "transaction_id":
            transaction_id,

        "transaction_number":
            transaction_number,

        "account_id":
            account_id,

        "customer_id":
            customer_id,

        "branch_id":
            branch_id,

        "transaction_date":
            transaction_datetime,

        "transaction_type":
            transaction_type,

        "transaction_category":
            transaction_category,

        "amount":
            amount,

        "currency":
            currency,

        "transaction_status":
            transaction_status,

        "channel":
            channel,

        "description":
            description
    }


    transactions.append(
        transaction
    )


    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if transaction_id % 50000 == 0:

        print(
            f"Transactions Generated : "
            f"{transaction_id:,}"
        )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    transactions
)


# ============================================================
# SORT TRANSACTIONS CHRONOLOGICALLY
# ============================================================
#
# Important:
# Balance calculations must follow transaction date.
# Therefore transactions are sorted by:
#
# 1. Account
# 2. Transaction Date
# 3. Transaction ID
#
# ============================================================

df = df.sort_values(
    by=[
        "account_id",
        "transaction_date",
        "transaction_id"
    ]
).reset_index(
    drop=True
)


# ============================================================
# REBUILD BALANCES CHRONOLOGICALLY
# ============================================================

print()
print("============================================================")
print("CALCULATING CHRONOLOGICAL ACCOUNT BALANCES")
print("============================================================")


# Create a fresh initial balance for every account.

initial_balances = {

    int(account["account_id"]):
        round(
            random.uniform(
                1000,
                50000
            ),
            2
        )

    for account in account_records
}


running_balances = initial_balances.copy()


balance_results = []


credit_transaction_types = [
    "Deposit",
    "Interest",
    "Refund"
]


debit_transaction_types = [
    "Withdrawal",
    "Transfer",
    "Payment",
    "Fee"
]


for row in df.itertuples(
    index=False
):

    account_id = int(
        row.account_id
    )


    current_balance = running_balances[
        account_id
    ]


    if row.transaction_status == "Completed":

        if row.transaction_type in credit_transaction_types:

            current_balance += row.amount


        elif row.transaction_type in debit_transaction_types:

            current_balance -= row.amount


    current_balance = round(
        current_balance,
        2
    )


    running_balances[
        account_id
    ] = current_balance


    balance_results.append(
        current_balance
    )


# ============================================================
# REBUILD BALANCES CHRONOLOGICALLY
# ============================================================

print()
print("============================================================")
print("CALCULATING CHRONOLOGICAL ACCOUNT BALANCES")
print("============================================================")


# ------------------------------------------------------------
# Create starting balance for each account
# ------------------------------------------------------------

initial_balances = {

    int(account["account_id"]):
        round(
            random.uniform(
                1000,
                50000
            ),
            2
        )

    for account in account_records
}


running_balances = initial_balances.copy()


balance_results = []


credit_transaction_types = [
    "Deposit",
    "Interest",
    "Refund"
]


debit_transaction_types = [
    "Withdrawal",
    "Transfer",
    "Payment",
    "Fee"
]


# ------------------------------------------------------------
# IMPORTANT
# Transactions are already sorted by:
# account_id
# transaction_date
# transaction_id
# ------------------------------------------------------------

for index, row in df.iterrows():

    account_id = int(
        row["account_id"]
    )

    current_balance = running_balances[
        account_id
    ]


    transaction_type = row[
        "transaction_type"
    ]

    transaction_status = row[
        "transaction_status"
    ]

    amount = float(
        row["amount"]
    )


    # --------------------------------------------------------
    # CREDIT TRANSACTIONS
    # --------------------------------------------------------

    if (
        transaction_status == "Completed"
        and transaction_type in credit_transaction_types
    ):

        current_balance += amount


    # --------------------------------------------------------
    # DEBIT TRANSACTIONS
    # --------------------------------------------------------

    elif (
        transaction_status == "Completed"
        and transaction_type in debit_transaction_types
    ):

        # ----------------------------------------------------
        # Do NOT allow a completed transaction to make the
        # account balance negative.
        # ----------------------------------------------------

        if amount <= current_balance:

            current_balance -= amount

        else:

            # Insufficient funds.
            # Mark transaction as Failed and leave balance
            # unchanged.

            df.at[
                index,
                "transaction_status"
            ] = "Failed"


    # --------------------------------------------------------
    # ROUND BALANCE
    # --------------------------------------------------------

    current_balance = round(
        current_balance,
        2
    )


    # --------------------------------------------------------
    # SAVE CURRENT ACCOUNT BALANCE
    # --------------------------------------------------------

    running_balances[
        account_id
    ] = current_balance


    balance_results.append(
        current_balance
    )


# ------------------------------------------------------------
# Add calculated balance to DataFrame
# ------------------------------------------------------------

df["balance_after_transaction"] = (
    balance_results
)

negative_balances = (
    df["balance_after_transaction"] < 0
).sum()

if negative_balances > 0:

    print()
    print("ERROR: Negative account balances found.")

    cursor.close()
    conn.close()
    raise SystemExit(1)


# ============================================================
# DATA VALIDATION
# ============================================================

print()
print("============================================================")
print("TRANSACTION DATA VALIDATION")
print("============================================================")


# ------------------------------------------------------------
# TOTAL RECORDS
# ------------------------------------------------------------

print()

total_transactions = len(df)

print(
    "Total Transactions :",
    total_transactions
)


# ------------------------------------------------------------
# REQUIRED TRANSACTION COLUMNS
# ------------------------------------------------------------

required_transaction_columns = [

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


missing_transaction_columns = [

    column

    for column in required_transaction_columns

    if column not in df.columns
]


print()

print(
    "Missing Transaction Columns :",
    missing_transaction_columns
)


# ------------------------------------------------------------
# NULL VALIDATION
# ------------------------------------------------------------

null_counts = (
    df[
        required_transaction_columns
    ]
    .isnull()
    .sum()
)


total_nulls = (
    null_counts.sum()
)


print()

print(
    "Total NULL Values :",
    total_nulls
)


if total_nulls > 0:

    print()

    print(
        "NULL values found:"
    )

    print(
        null_counts[
            null_counts > 0
        ]
    )


# ------------------------------------------------------------
# DUPLICATE TRANSACTION IDS
# ------------------------------------------------------------

duplicate_transaction_ids = (

    df["transaction_id"]
    .duplicated()
    .sum()
)


print()

print(
    "Duplicate Transaction IDs :",
    duplicate_transaction_ids
)


# ------------------------------------------------------------
# DUPLICATE TRANSACTION NUMBERS
# ------------------------------------------------------------

duplicate_transaction_numbers = (

    df["transaction_number"]
    .duplicated()
    .sum()
)


print()

print(
    "Duplicate Transaction Numbers :",
    duplicate_transaction_numbers
)


# ------------------------------------------------------------
# INVALID ACCOUNT IDS
# ------------------------------------------------------------

valid_account_ids = set(
    accounts["account_id"]
)


invalid_account_ids = (

    ~df["account_id"]
    .isin(valid_account_ids)
).sum()


print()

print(
    "Invalid Account IDs :",
    invalid_account_ids
)


# ------------------------------------------------------------
# INVALID CUSTOMER IDS
# ------------------------------------------------------------

valid_customer_ids = set(
    accounts["customer_id"]
)


invalid_customer_ids = (

    ~df["customer_id"]
    .isin(valid_customer_ids)
).sum()


print()

print(
    "Invalid Customer IDs :",
    invalid_customer_ids
)


# ------------------------------------------------------------
# INVALID BRANCH IDS
# ------------------------------------------------------------

valid_branch_ids = set(
    accounts["branch_id"]
)


invalid_branch_ids = (

    ~df["branch_id"]
    .isin(valid_branch_ids)
).sum()


print()

print(
    "Invalid Branch IDs :",
    invalid_branch_ids
)


# ------------------------------------------------------------
# INVALID AMOUNTS
# ------------------------------------------------------------

invalid_amounts = (

    df["amount"] <= 0
).sum()


print()

print(
    "Invalid Transaction Amounts :",
    invalid_amounts
)


# ------------------------------------------------------------
# FUTURE TRANSACTION DATES
# ------------------------------------------------------------

current_datetime = datetime.now()


invalid_future_dates = (

    df["transaction_date"]
    > current_datetime
).sum()


print()

print(
    "Future Transaction Dates :",
    invalid_future_dates
)


# ------------------------------------------------------------
# INVALID TRANSACTION TYPES
# ------------------------------------------------------------

invalid_transaction_types = (

    ~df["transaction_type"]
    .isin(transaction_types)
).sum()


print()

print(
    "Invalid Transaction Types :",
    invalid_transaction_types
)


# ------------------------------------------------------------
# INVALID TRANSACTION STATUSES
# ------------------------------------------------------------

invalid_transaction_statuses = (

    ~df["transaction_status"]
    .isin(transaction_statuses)
).sum()


print()

print(
    "Invalid Transaction Statuses :",
    invalid_transaction_statuses
)


# ------------------------------------------------------------
# INVALID CHANNELS
# ------------------------------------------------------------

invalid_channels = (

    ~df["channel"]
    .isin(channels)
).sum()


print()

print(
    "Invalid Transaction Channels :",
    invalid_channels
)


# ------------------------------------------------------------
# INVALID CURRENCY
# ------------------------------------------------------------

invalid_currency = (

    df["currency"] != currency
).sum()


print()

print(
    "Invalid Currency Values :",
    invalid_currency
)


# ------------------------------------------------------------
# BALANCE VALIDATION
# ------------------------------------------------------------

null_balances = (

    df["balance_after_transaction"]
    .isnull()
    .sum()
)


negative_balances = (

    df["balance_after_transaction"] < 0
).sum()


print()

print(
    "NULL Balance Values :",
    null_balances
)


print(
    "Negative Balances   :",
    negative_balances
)


# ============================================================
# TRANSACTION TYPE DISTRIBUTION
# ============================================================

print()
print("============================================================")
print("TRANSACTION TYPE DISTRIBUTION")
print("============================================================")

print(
    df["transaction_type"]
    .value_counts()
)


# ============================================================
# TRANSACTION STATUS DISTRIBUTION
# ============================================================

print()
print("============================================================")
print("TRANSACTION STATUS DISTRIBUTION")
print("============================================================")

print(
    df["transaction_status"]
    .value_counts()
)


# ============================================================
# CHANNEL DISTRIBUTION
# ============================================================

print()
print("============================================================")
print("TRANSACTION CHANNEL DISTRIBUTION")
print("============================================================")

print(
    df["channel"]
    .value_counts()
)


# ============================================================
# SAMPLE DATA
# ============================================================

print()
print("============================================================")
print("SAMPLE TRANSACTIONS")
print("============================================================")

print(
    df.head(10).to_string(
        index=False
    )
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

output_directory = os.path.dirname(
    OUTPUT_FILE
)


if output_directory:

    os.makedirs(
        output_directory,
        exist_ok=True
    )


# ============================================================
# SAVE CSV
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL VALIDATION
# ============================================================

validation_passed = (

    len(df)
    == NUMBER_OF_TRANSACTIONS

    and duplicate_transaction_ids
    == 0

    and duplicate_transaction_numbers
    == 0

    and invalid_account_ids
    == 0

    and invalid_customer_ids
    == 0

    and invalid_branch_ids
    == 0

    and invalid_amounts
    == 0

    and invalid_future_dates
    == 0

    and invalid_transaction_types
    == 0

    and invalid_transaction_statuses
    == 0

    and invalid_channels
    == 0

    and invalid_currency
    == 0

    and total_nulls
    == 0

    and null_balances
    == 0

    and negative_balances
    == 0
)


print()
print("============================================================")


if validation_passed:

    print(
        "TRANSACTION DATA VALIDATION PASSED"
    )

    print(
        "Transactions CSV Generated Successfully"
    )

else:

    print(
        "TRANSACTION DATA VALIDATION FAILED"
    )


print("============================================================")

print()

print(
    "File :",
    OUTPUT_FILE
)


print(
    "Rows :",
    len(df)
)


print()

print(
    "Transaction Generation Completed"
)

print("============================================================")