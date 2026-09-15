"""
generate_loans.py

Enterprise Banking Data Warehouse
Loan Data Generator

Generates:
    data/raw/loans.csv
"""

import random
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_OF_LOANS = 500000

OUTPUT_FILE = Path("data/raw/loans.csv")

CUSTOMERS_FILE = Path("data/raw/customers.csv")
ACCOUNTS_FILE = Path("data/raw/accounts.csv")

RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ============================================================
# MASTER VALUES
# These values match the PostgreSQL loan constraints
# ============================================================

LOAN_TYPES = [
    "Personal",
    "Auto",
    "Mortgage",
    "Business",
    "Student"
]

LOAN_TYPE_WEIGHTS = [
    30,
    25,
    20,
    15,
    10
]


LOAN_STATUSES = [
    "Active",
    "Approved",
    "Defaulted",
    "Paid Off",
    "Pending",
    "Rejected"
]

LOAN_STATUS_WEIGHTS = [
    38,
    20,
    7,
    15,
    12,
    8
]


LOAN_TERMS = {
    "Personal": [12, 24, 36, 48, 60],
    "Auto": [36, 48, 60, 72, 84],
    "Mortgage": [120, 180, 240, 360],
    "Business": [12, 24, 36, 48, 60, 84],
    "Student": [60, 120, 180, 240]
}


# ============================================================
# HELPER FUNCTION
# ============================================================

def print_section(title):
    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


# ============================================================
# READ CUSTOMERS
# ============================================================

print_section("READING CUSTOMER DATA")

if not CUSTOMERS_FILE.exists():
    print("ERROR: Customers CSV not found.")
    print("File:", CUSTOMERS_FILE)
    raise SystemExit(1)


customers = pd.read_csv(CUSTOMERS_FILE)


if customers.empty:
    print("ERROR: Customers CSV is empty.")
    raise SystemExit(1)


print("Customers Loaded Successfully")
print("Total Customers :", len(customers))


# ============================================================
# CUSTOMER ID VALIDATION
# ============================================================

if "customer_id" not in customers.columns:

    print()
    print("ERROR: customer_id column not found in customers.csv")
    print("Available columns:", list(customers.columns))

    raise SystemExit(1)


customers["customer_id"] = pd.to_numeric(
    customers["customer_id"],
    errors="coerce"
)

customers = customers.dropna(
    subset=["customer_id"]
)

customers["customer_id"] = (
    customers["customer_id"]
    .astype("int64")
)


valid_customer_ids = (
    customers["customer_id"]
    .drop_duplicates()
    .tolist()
)


if not valid_customer_ids:
    print("ERROR: No valid customer IDs found.")
    raise SystemExit(1)


print("Valid Customer IDs :", len(valid_customer_ids))


# ============================================================
# READ ACCOUNTS
#
# We intentionally use accounts.csv for branch_id because
# accounts.csv already contains the actual branch_id values
# used by the banking data model.
# ============================================================

print_section("READING ACCOUNT DATA")

if not ACCOUNTS_FILE.exists():
    print("ERROR: Accounts CSV not found.")
    print("File:", ACCOUNTS_FILE)
    raise SystemExit(1)


accounts = pd.read_csv(ACCOUNTS_FILE)


if accounts.empty:
    print("ERROR: Accounts CSV is empty.")
    raise SystemExit(1)


print("Accounts Loaded Successfully")
print("Total Accounts :", len(accounts))


# ============================================================
# ACCOUNT REQUIRED COLUMNS
# ============================================================

required_account_columns = [
    "account_id",
    "branch_id"
]


missing_account_columns = [
    column
    for column in required_account_columns
    if column not in accounts.columns
]


if missing_account_columns:

    print()
    print("ERROR: Missing required account columns:")

    for column in missing_account_columns:
        print(" -", column)

    print()
    print("Available columns:", list(accounts.columns))

    raise SystemExit(1)


# ============================================================
# CLEAN ACCOUNT IDS
# ============================================================

accounts["account_id"] = pd.to_numeric(
    accounts["account_id"],
    errors="coerce"
)

accounts["branch_id"] = pd.to_numeric(
    accounts["branch_id"],
    errors="coerce"
)


accounts = accounts.dropna(
    subset=[
        "account_id",
        "branch_id"
    ]
)


accounts["account_id"] = (
    accounts["account_id"]
    .astype("int64")
)

accounts["branch_id"] = (
    accounts["branch_id"]
    .astype("int64")
)


# ============================================================
# VALID BRANCH IDS
# ============================================================

valid_branch_ids = (
    accounts["branch_id"]
    .drop_duplicates()
    .tolist()
)


if not valid_branch_ids:

    print()
    print("ERROR: No valid branch IDs found in accounts.csv.")

    raise SystemExit(1)


print("Valid Branch IDs :", len(valid_branch_ids))


# ============================================================
# GENERATING LOANS
# ============================================================

print_section("GENERATING LOANS")

print(
    "Loans To Generate :",
    f"{NUMBER_OF_LOANS:,}"
)


# ============================================================
# LOAN IDS
# ============================================================

loan_ids = np.arange(
    1,
    NUMBER_OF_LOANS + 1,
    dtype=np.int64
)


# ============================================================
# LOAN NUMBERS
# ============================================================

loan_numbers = [
    f"LN{loan_id:09d}"
    for loan_id in loan_ids
]


# ============================================================
# CUSTOMER IDs
# ============================================================

generated_customer_ids = np.random.choice(
    valid_customer_ids,
    size=NUMBER_OF_LOANS
)


# ============================================================
# BRANCH IDs
# ============================================================

generated_branch_ids = np.random.choice(
    valid_branch_ids,
    size=NUMBER_OF_LOANS
)


# ============================================================
# LOAN TYPES
# ============================================================

generated_loan_types = np.random.choice(
    LOAN_TYPES,
    size=NUMBER_OF_LOANS,
    p=np.array(LOAN_TYPE_WEIGHTS) / sum(LOAN_TYPE_WEIGHTS)
)


# ============================================================
# LOAN AMOUNTS
# ============================================================

loan_amounts = np.random.lognormal(
    mean=np.log(25000),
    sigma=0.9,
    size=NUMBER_OF_LOANS
)


loan_amounts = np.clip(
    loan_amounts,
    1000,
    500000
)


loan_amounts = np.round(
    loan_amounts,
    2
)


# ============================================================
# INTEREST RATES
# ============================================================

interest_rates = np.random.uniform(
    2.50,
    18.00,
    NUMBER_OF_LOANS
)


interest_rates = np.round(
    interest_rates,
    2
)


# ============================================================
# LOAN TERMS
# ============================================================

loan_term_months = np.array(
    [
        random.choice(
            LOAN_TERMS[loan_type]
        )
        for loan_type in generated_loan_types
    ],
    dtype=np.int64
)


# ============================================================
# START DATES
# ============================================================

start_date_start = datetime(
    2016,
    1,
    1
)

start_date_end = datetime(
    2026,
    1,
    1
)


total_days = (
    start_date_end -
    start_date_start
).days


start_dates = [
    start_date_start +
    timedelta(
        days=random.randint(
            0,
            total_days
        )
    )
    for _ in range(NUMBER_OF_LOANS)
]


# ============================================================
# MATURITY DATES
# ============================================================

maturity_dates = [
    pd.Timestamp(start_date) +
    pd.DateOffset(
        months=int(term)
    )
    for start_date, term
    in zip(
        start_dates,
        loan_term_months
    )
]


# ============================================================
# LOAN STATUS
# ============================================================

generated_loan_statuses = np.random.choice(
    LOAN_STATUSES,
    size=NUMBER_OF_LOANS,
    p=np.array(LOAN_STATUS_WEIGHTS) /
      sum(LOAN_STATUS_WEIGHTS)
)


# ============================================================
# OUTSTANDING BALANCE
# ============================================================

outstanding_balances = (
    loan_amounts *
    np.random.uniform(
        0.05,
        0.95,
        NUMBER_OF_LOANS
    )
)


outstanding_balances = np.round(
    outstanding_balances,
    2
)


# ============================================================
# STATUS-SPECIFIC BALANCES
# ============================================================

for index, status in enumerate(
    generated_loan_statuses
):

    if status == "Paid Off":

        outstanding_balances[index] = 0.00


    elif status == "Rejected":

        outstanding_balances[index] = 0.00


    elif status == "Pending":

        outstanding_balances[index] = round(
            loan_amounts[index] *
            random.uniform(
                0.80,
                1.00
            ),
            2
        )


    elif status == "Approved":

        outstanding_balances[index] = round(
            loan_amounts[index] *
            random.uniform(
                0.75,
                1.00
            ),
            2
        )


    elif status == "Defaulted":

        outstanding_balances[index] = round(
            loan_amounts[index] *
            random.uniform(
                0.25,
                1.00
            ),
            2
        )


    elif status == "Active":

        outstanding_balances[index] = round(
            loan_amounts[index] *
            random.uniform(
                0.05,
                0.95
            ),
            2
        )


# ============================================================
# MONTHLY PAYMENT
# ============================================================

monthly_payments = []


for amount, rate, term in zip(
    loan_amounts,
    interest_rates,
    loan_term_months
):

    monthly_rate = (
        rate / 100 / 12
    )


    if monthly_rate == 0:

        payment = (
            amount / term
        )

    else:

        payment = (
            amount *
            monthly_rate *
            (1 + monthly_rate) ** term
            /
            (
                (1 + monthly_rate) ** term
                - 1
            )
        )


    monthly_payments.append(
        round(
            payment,
            2
        )
    )


monthly_payments = np.array(
    monthly_payments
)


# ============================================================
# CREATED / UPDATED TIMESTAMPS
# ============================================================

created_at_values = []

updated_at_values = []


current_datetime = datetime.now()


for start_date in start_dates:

    created_date = (
        start_date -
        timedelta(
            days=random.randint(
                0,
                30
            )
        )
    )


    updated_date = (
        created_date +
        timedelta(
            days=random.randint(
                0,
                365
            )
        )
    )


    if updated_date > current_datetime:

        updated_date = current_datetime


    created_at_values.append(
        created_date
    )

    updated_at_values.append(
        updated_date
    )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    {
        "loan_id":
            loan_ids,

        "loan_number":
            loan_numbers,

        "customer_id":
            generated_customer_ids,

        "branch_id":
            generated_branch_ids,

        "loan_type":
            generated_loan_types,

        "loan_amount":
            loan_amounts,

        "outstanding_balance":
            outstanding_balances,

        "interest_rate":
            interest_rates,

        "loan_term_months":
            loan_term_months,

        "monthly_payment":
            monthly_payments,

        "start_date":
            start_dates,

        "maturity_date":
            maturity_dates,

        "loan_status":
            generated_loan_statuses,

        "created_at":
            created_at_values,

        "updated_at":
            updated_at_values
    }
)


# ============================================================
# DATA VALIDATION
# ============================================================

print_section("LOAN DATA VALIDATION")


validation_passed = True


# ============================================================
# TOTAL RECORDS
# ============================================================

print(
    "Total Loans :",
    len(df)
)


if len(df) != NUMBER_OF_LOANS:

    print(
        "ERROR: Incorrect number of loans generated."
    )

    validation_passed = False


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "loan_id",
    "loan_number",
    "customer_id",
    "branch_id",
    "loan_type",
    "loan_amount",
    "outstanding_balance",
    "interest_rate",
    "loan_term_months",
    "start_date",
    "maturity_date",
    "loan_status"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print()
    print(
        "Missing Required Columns :",
        missing_columns
    )

    validation_passed = False

else:

    print(
        "Required Loan Columns Validation Passed"
    )


# ============================================================
# NULL VALUES
# ============================================================

null_values = (
    df[required_columns]
    .isnull()
    .sum()
    .sum()
)


print(
    "NULL Values In Required Columns :",
    null_values
)


if null_values > 0:

    validation_passed = False


# ============================================================
# DUPLICATE LOAN IDs
# ============================================================

duplicate_loan_ids = (
    df["loan_id"]
    .duplicated()
    .sum()
)


print(
    "Duplicate Loan IDs :",
    duplicate_loan_ids
)


if duplicate_loan_ids > 0:

    validation_passed = False


# ============================================================
# DUPLICATE LOAN NUMBERS
# ============================================================

duplicate_loan_numbers = (
    df["loan_number"]
    .duplicated()
    .sum()
)


print(
    "Duplicate Loan Numbers :",
    duplicate_loan_numbers
)


if duplicate_loan_numbers > 0:

    validation_passed = False


# ============================================================
# INVALID CUSTOMER IDs
# ============================================================

invalid_customer_ids = (
    ~df["customer_id"]
    .isin(valid_customer_ids)
).sum()


print(
    "Invalid Customer IDs :",
    invalid_customer_ids
)


if invalid_customer_ids > 0:

    validation_passed = False


# ============================================================
# INVALID BRANCH IDs
# ============================================================

invalid_branch_ids = (
    ~df["branch_id"]
    .isin(valid_branch_ids)
).sum()


print(
    "Invalid Branch IDs :",
    invalid_branch_ids
)


if invalid_branch_ids > 0:

    validation_passed = False


# ============================================================
# INVALID LOAN TYPES
# ============================================================

invalid_loan_types = (
    ~df["loan_type"]
    .isin(LOAN_TYPES)
).sum()


print(
    "Invalid Loan Types :",
    invalid_loan_types
)


if invalid_loan_types > 0:

    validation_passed = False


# ============================================================
# INVALID LOAN STATUSES
# ============================================================

invalid_loan_statuses = (
    ~df["loan_status"]
    .isin(LOAN_STATUSES)
).sum()


print(
    "Invalid Loan Statuses :",
    invalid_loan_statuses
)


if invalid_loan_statuses > 0:

    validation_passed = False


# ============================================================
# INVALID LOAN AMOUNTS
# ============================================================

invalid_loan_amounts = (
    df["loan_amount"] <= 0
).sum()


print(
    "Invalid Loan Amounts :",
    invalid_loan_amounts
)


if invalid_loan_amounts > 0:

    validation_passed = False


# ============================================================
# INVALID INTEREST RATES
# ============================================================

invalid_interest_rates = (
    df["interest_rate"] < 0
).sum()


print(
    "Invalid Interest Rates :",
    invalid_interest_rates
)


if invalid_interest_rates > 0:

    validation_passed = False


# ============================================================
# INVALID LOAN TERMS
# ============================================================

invalid_terms = (
    df["loan_term_months"] <= 0
).sum()


print(
    "Invalid Loan Terms :",
    invalid_terms
)


if invalid_terms > 0:

    validation_passed = False


# ============================================================
# INVALID OUTSTANDING BALANCES
# ============================================================

invalid_outstanding_balances = (
    (
        df["outstanding_balance"] < 0
    )
    |
    (
        df["outstanding_balance"]
        > df["loan_amount"]
    )
).sum()


print(
    "Invalid Outstanding Balances :",
    invalid_outstanding_balances
)


if invalid_outstanding_balances > 0:

    validation_passed = False


# ============================================================
# INVALID MATURITY DATES
# ============================================================

invalid_maturity_dates = (
    df["maturity_date"]
    <= df["start_date"]
).sum()


print(
    "Invalid Maturity Dates :",
    invalid_maturity_dates
)


if invalid_maturity_dates > 0:

    validation_passed = False


# ============================================================
# INVALID UPDATED DATES
# ============================================================

invalid_updated_dates = (
    df["updated_at"]
    < df["created_at"]
).sum()


print(
    "Invalid Updated Dates :",
    invalid_updated_dates
)


if invalid_updated_dates > 0:

    validation_passed = False


# ============================================================
# SAMPLE DATA
# ============================================================

print_section("SAMPLE LOANS")

print(
    df.head(5).to_string(
        index=False
    )
)


# ============================================================
# STOP IF VALIDATION FAILS
# ============================================================

if not validation_passed:

    print()
    print("=" * 65)
    print("LOAN DATA VALIDATION FAILED")
    print("=" * 65)

    raise SystemExit(1)


# ============================================================
# VALIDATION PASSED
# ============================================================

print()
print("=" * 65)
print("LOAN DATA VALIDATION PASSED")
print("=" * 65)


# ============================================================
# WRITE CSV
# ============================================================

print_section("WRITING LOANS CSV")


OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


try:

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        date_format="%Y-%m-%d %H:%M:%S"
    )

except Exception as exc:

    print()
    print("ERROR: Failed to write loans CSV.")
    print("DETAIL:", exc)

    raise SystemExit(1)


# ============================================================
# VERIFY GENERATED CSV
# ============================================================

try:

    generated_file = pd.read_csv(
        OUTPUT_FILE
    )

except Exception as exc:

    print()
    print("ERROR: Unable to read generated loans CSV.")
    print("DETAIL:", exc)

    raise SystemExit(1)


# ============================================================
# FINAL FILE VALIDATION
# ============================================================

print()
print("=" * 65)
print("LOANS CSV GENERATED SUCCESSFULLY")
print("=" * 65)

print(
    "File :",
    OUTPUT_FILE
)

print(
    "Rows :",
    f"{len(generated_file):,}"
)

print(
    "Columns :",
    len(generated_file.columns)
)


if len(generated_file) != NUMBER_OF_LOANS:

    print()
    print("ERROR: Generated CSV row count is incorrect.")

    raise SystemExit(1)


print("=" * 65)


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 65)
print("Loan Generation Completed")
print("=" * 65)