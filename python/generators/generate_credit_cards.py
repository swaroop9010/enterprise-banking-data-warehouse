"""
Enterprise Banking DW
Credit Card Data Generator

Generates synthetic credit card data for the Enterprise Banking Data Warehouse.

Output:
    data/raw/credit_cards.csv

Records:
    500,000
"""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "raw"

CUSTOMERS_FILE = DATA_DIR / "customers.csv"
ACCOUNTS_FILE = DATA_DIR / "accounts.csv"
OUTPUT_FILE = DATA_DIR / "credit_cards.csv"

TOTAL_CARDS = 500_000

RANDOM_SEED = 42

random.seed(RANDOM_SEED)


# ============================================================
# CREDIT CARD BUSINESS VALUES
# ============================================================

CARD_TYPES = [
    "Personal",
    "Business",
    "Platinum",
    "Gold",
]

CARD_NETWORKS = [
    "Visa",
    "Mastercard",
    "American Express",
    "Discover",
]

CARD_STATUSES = [
    "Active",
    "Blocked",
    "Expired",
    "Closed",
]

CREDIT_LIMITS = [
    1000,
    2500,
    5000,
    7500,
    10000,
    15000,
    25000,
    50000,
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def print_header(title: str) -> None:
    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


def find_column(df: pd.DataFrame, candidates: list[str], description: str) -> str:
    """
    Find a matching column from a list of possible column names.
    Matching is case-insensitive.
    """

    lookup = {str(col).strip().lower(): col for col in df.columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    raise ValueError(
        f"Could not find a valid {description} column.\n"
        f"Expected one of: {candidates}\n"
        f"Available columns: {list(df.columns)}"
    )


def generate_card_number(card_id: int) -> str:
    """
    Generate a deterministic 16-digit card number.

    The generated number is guaranteed to be unique within this run.
    """

    # Common card prefixes.
    prefix = random.choice(
        [
            "4",    # Visa
            "5",    # Mastercard
            "6",    # Discover
        ]
    )

    # 15 remaining digits.
    remaining = "".join(random.choices(string.digits, k=15))

    return prefix + remaining


def generate_issue_date() -> datetime.date:
    """
    Generate an issue date between 2018-01-01 and today.
    """

    start_date = datetime(2018, 1, 1)
    end_date = datetime.now()

    days_range = (end_date - start_date).days

    return (start_date + timedelta(days=random.randint(0, days_range))).date()


def generate_created_at(issue_date) -> datetime:
    """
    created_at should not be earlier than issue_date.
    """

    issue_datetime = datetime.combine(issue_date, datetime.min.time())

    current_datetime = datetime.now()

    if issue_datetime >= current_datetime:
        return current_datetime

    seconds_range = int(
        (current_datetime - issue_datetime).total_seconds()
    )

    return issue_datetime + timedelta(
        seconds=random.randint(0, max(seconds_range, 1))
    )


# ============================================================
# READ CUSTOMER DATA
# ============================================================

print_header("READING CUSTOMER DATA")

if not CUSTOMERS_FILE.exists():
    raise FileNotFoundError(
        f"Customers CSV not found:\n{CUSTOMERS_FILE}"
    )

customers_df = pd.read_csv(CUSTOMERS_FILE)

customer_id_col = find_column(
    customers_df,
    ["customer_id", "id"],
    "Customer ID"
)

customer_ids = (
    customers_df[customer_id_col]
    .dropna()
    .drop_duplicates()
    .tolist()
)

if not customer_ids:
    raise ValueError("No valid customer IDs were found.")

print("Customers Loaded Successfully")
print(f"Total Customers : {len(customers_df):,}")
print(f"Valid Customer IDs : {len(customer_ids):,}")


# ============================================================
# READ ACCOUNT DATA
# ============================================================

print_header("READING ACCOUNT DATA")

if not ACCOUNTS_FILE.exists():
    raise FileNotFoundError(
        f"Accounts CSV not found:\n{ACCOUNTS_FILE}"
    )

accounts_df = pd.read_csv(ACCOUNTS_FILE)

account_id_col = find_column(
    accounts_df,
    ["account_id", "id"],
    "Account ID"
)

account_customer_id_col = find_column(
    accounts_df,
    ["customer_id"],
    "Account Customer ID"
)

account_relationships = (
    accounts_df[
        [account_id_col, account_customer_id_col]
    ]
    .dropna()
    .drop_duplicates()
    .copy()
)

# Keep only accounts whose customer exists.
valid_customer_set = set(customer_ids)

account_relationships = account_relationships[
    account_relationships[account_customer_id_col].isin(valid_customer_set)
]

if account_relationships.empty:
    raise ValueError(
        "No valid Account ID / Customer ID relationships were found."
    )

account_relationships = list(
    account_relationships[
        [account_id_col, account_customer_id_col]
    ].itertuples(index=False, name=None)
)

print("Accounts Loaded Successfully")
print(f"Total Accounts : {len(accounts_df):,}")
print(
    f"Valid Account / Customer Relationships : "
    f"{len(account_relationships):,}"
)


# ============================================================
# GENERATE CREDIT CARDS
# ============================================================

print_header("GENERATING CREDIT CARDS")

print(f"Credit Cards To Generate : {TOTAL_CARDS:,}")

generated_rows = []

used_card_numbers: set[str] = set()

for card_id in range(1, TOTAL_CARDS + 1):

    account_id, customer_id = random.choice(account_relationships)

    # --------------------------------------------------------
    # Unique card number
    # --------------------------------------------------------

    card_number = generate_card_number(card_id)

    while card_number in used_card_numbers:
        card_number = generate_card_number(card_id)

    used_card_numbers.add(card_number)

    # --------------------------------------------------------
    # Card attributes
    # --------------------------------------------------------

    card_type = random.choice(CARD_TYPES)

    card_network = random.choice(CARD_NETWORKS)

    card_status = random.choices(
        CARD_STATUSES,
        weights=[80, 7, 5, 8],
        k=1
    )[0]

    # --------------------------------------------------------
    # Financial values
    # --------------------------------------------------------

    credit_limit = random.choice(CREDIT_LIMITS)

    outstanding_balance = round(
        random.uniform(
            0,
            credit_limit * 0.80
        ),
        2
    )

    available_credit = round(
        credit_limit - outstanding_balance,
        2
    )

    # Prevent negative available credit from rounding issues.
    available_credit = max(available_credit, 0)

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    issue_date = generate_issue_date()

    expiry_date = issue_date.replace(
        year=issue_date.year + 4
    )

    created_at = generate_created_at(issue_date)

    # --------------------------------------------------------
    # Store record
    # --------------------------------------------------------

    generated_rows.append(
        {
            "card_id": card_id,
            "customer_id": customer_id,
            "account_id": account_id,
            "card_number": card_number,
            "card_type": card_type,
            "card_network": card_network,
            "credit_limit": credit_limit,
            "available_credit": available_credit,
            "outstanding_balance": outstanding_balance,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "card_status": card_status,
            "created_at": created_at,
        }
    )

    if card_id % 50_000 == 0:
        print(
            f"Credit Cards Generated : {card_id:,}"
        )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(generated_rows)


# ============================================================
# FINAL DATA VALIDATION
# ============================================================

print_header("CREDIT CARD DATA VALIDATION")

validation_passed = True


# ------------------------------------------------------------
# 1. Record count
# ------------------------------------------------------------

print(
    f"Total Credit Cards : {len(df):,}"
)

if len(df) != TOTAL_CARDS:
    print("ERROR: Incorrect number of credit card records.")
    validation_passed = False


# ------------------------------------------------------------
# 2. Required columns
# ------------------------------------------------------------

required_columns = [
    "card_id",
    "customer_id",
    "account_id",
    "card_number",
    "card_type",
    "card_network",
    "credit_limit",
    "available_credit",
    "outstanding_balance",
    "issue_date",
    "expiry_date",
    "card_status",
    "created_at",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print(
        "ERROR: Missing required columns:"
    )

    for column in missing_columns:
        print(f" - {column}")

    validation_passed = False
else:
    print("Required Columns Validation Passed")


# ------------------------------------------------------------
# 3. NULL validation
# ------------------------------------------------------------

required_non_null = [
    "card_id",
    "customer_id",
    "account_id",
    "card_number",
    "card_type",
    "card_network",
    "credit_limit",
    "available_credit",
    "issue_date",
    "expiry_date",
]

null_count = df[required_non_null].isnull().sum().sum()

print(
    f"NULL Values In Required Columns : {null_count:,}"
)

if null_count > 0:
    print("ERROR: NULL values found in required columns.")
    validation_passed = False


# ------------------------------------------------------------
# 4. Duplicate Card IDs
# ------------------------------------------------------------

duplicate_card_ids = (
    df["card_id"].duplicated().sum()
)

print(
    f"Duplicate Card IDs : {duplicate_card_ids:,}"
)

if duplicate_card_ids > 0:
    validation_passed = False


# ------------------------------------------------------------
# 5. Duplicate Card Numbers
# ------------------------------------------------------------

duplicate_card_numbers = (
    df["card_number"].duplicated().sum()
)

print(
    f"Duplicate Card Numbers : "
    f"{duplicate_card_numbers:,}"
)

if duplicate_card_numbers > 0:
    validation_passed = False


# ------------------------------------------------------------
# 6. Card number format
# ------------------------------------------------------------

invalid_card_numbers = (
    ~df["card_number"]
    .astype(str)
    .str.fullmatch(r"\d{16}")
).sum()

print(
    f"Invalid Card Numbers : {invalid_card_numbers:,}"
)

if invalid_card_numbers > 0:
    validation_passed = False


# ------------------------------------------------------------
# 7. Credit limit validation
# ------------------------------------------------------------

invalid_credit_limits = (
    df["credit_limit"] <= 0
).sum()

print(
    f"Invalid Credit Limits : "
    f"{invalid_credit_limits:,}"
)

if invalid_credit_limits > 0:
    validation_passed = False


# ------------------------------------------------------------
# 8. Available credit validation
# ------------------------------------------------------------

invalid_available_credit = (
    (df["available_credit"] < 0)
    |
    (
        df["available_credit"]
        > df["credit_limit"]
    )
).sum()

print(
    f"Invalid Available Credit : "
    f"{invalid_available_credit:,}"
)

if invalid_available_credit > 0:
    validation_passed = False


# ------------------------------------------------------------
# 9. Outstanding balance validation
# ------------------------------------------------------------

invalid_outstanding_balance = (
    (df["outstanding_balance"] < 0)
    |
    (
        df["outstanding_balance"]
        > df["credit_limit"]
    )
).sum()

print(
    f"Invalid Outstanding Balances : "
    f"{invalid_outstanding_balance:,}"
)

if invalid_outstanding_balance > 0:
    validation_passed = False


# ------------------------------------------------------------
# 10. Balance consistency
# ------------------------------------------------------------

balance_mismatch = (
    (
        df["available_credit"]
        + df["outstanding_balance"]
        - df["credit_limit"]
    ).abs() > 0.01
).sum()

print(
    f"Balance Consistency Errors : "
    f"{balance_mismatch:,}"
)

if balance_mismatch > 0:
    validation_passed = False


# ------------------------------------------------------------
# 11. Issue / expiry date validation
# ------------------------------------------------------------

invalid_dates = (
    pd.to_datetime(df["expiry_date"])
    <= pd.to_datetime(df["issue_date"])
).sum()

print(
    f"Invalid Issue / Expiry Dates : "
    f"{invalid_dates:,}"
)

if invalid_dates > 0:
    validation_passed = False


# ------------------------------------------------------------
# 12. Customer relationship validation
# ------------------------------------------------------------

customer_id_set = set(customer_ids)

invalid_customer_ids = (
    ~df["customer_id"].isin(customer_id_set)
).sum()

print(
    f"Invalid Customer IDs : "
    f"{invalid_customer_ids:,}"
)

if invalid_customer_ids > 0:
    validation_passed = False


# ------------------------------------------------------------
# 13. Account relationship validation
# ------------------------------------------------------------

account_relationship_set = set(account_relationships)

invalid_account_relationships = 0

for account_id, customer_id in zip(
    df["account_id"],
    df["customer_id"]
):
    if (account_id, customer_id) not in account_relationship_set:
        invalid_account_relationships += 1

print(
    f"Invalid Account / Customer Relationships : "
    f"{invalid_account_relationships:,}"
)

if invalid_account_relationships > 0:
    validation_passed = False


# ============================================================
# SHOW SAMPLE DATA
# ============================================================

print_header("SAMPLE CREDIT CARDS")

print(
    df.head(5).to_string(index=False)
)


# ============================================================
# WRITE CSV
# ============================================================

if not validation_passed:
    print()
    print("CREDIT CARD DATA VALIDATION FAILED")
    raise SystemExit(1)


print_header("WRITING CREDIT CARDS CSV")

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# CSV VALIDATION
# ============================================================

print_header("FINAL CSV VALIDATION")

generated_file = pd.read_csv(OUTPUT_FILE)

print(
    f"File    : {OUTPUT_FILE}"
)

print(
    f"Rows    : {len(generated_file):,}"
)

print(
    f"Columns : {len(generated_file.columns):,}"
)

if len(generated_file) != TOTAL_CARDS:
    print()
    print(
        "ERROR: Generated CSV row count is incorrect."
    )

    raise SystemExit(1)

if list(generated_file.columns) != required_columns:
    print()
    print(
        "ERROR: Generated CSV columns are incorrect."
    )

    print(
        "Expected:"
    )
    print(required_columns)

    print(
        "Actual:"
    )
    print(list(generated_file.columns))

    raise SystemExit(1)


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 65)
print("CREDIT CARD DATA VALIDATION PASSED")
print("=" * 65)

print()
print("=" * 65)
print("CREDIT CARDS CSV GENERATED SUCCESSFULLY")
print("=" * 65)

print()
print(f"File : {OUTPUT_FILE}")
print(f"Rows : {len(generated_file):,}")
print(f"Columns : {len(generated_file.columns):,}")

print()
print("Credit Card Generation Completed")
print("=" * 65)