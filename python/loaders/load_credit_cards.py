"""
Enterprise Banking DW
Credit Card Data Loader

Loads:
    data/raw/credit_cards.csv

Into:
    public.credit_cards

Expected records:
    500,000
"""

from __future__ import annotations

import getpass
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CSV_FILE = BASE_DIR / "data" / "raw" / "credit_cards.csv"

DATABASE_NAME = "enterprisebankingdw"
DATABASE_USER = "postgres"
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432

TABLE_SCHEMA = "public"
TABLE_NAME = "credit_cards"

EXPECTED_RECORDS = 500_000

BATCH_SIZE = 5_000


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
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


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_header(title: str) -> None:
    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database():
    print_header("ENTERPRISE BANKING DW - CREDIT CARD LOAD")

    print_header("CONNECTING TO POSTGRESQL")

    password = getpass.getpass("Enter PostgreSQL password: ")

    conn = psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=password,
    )

    print("Database Connected Successfully")

    return conn


# ============================================================
# CHECK TABLE
# ============================================================

def validate_table(conn) -> None:

    print_header("CHECKING CREDIT CARD TABLE")

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_name = %s
            );
            """,
            (TABLE_SCHEMA, TABLE_NAME),
        )

        table_exists = cursor.fetchone()[0]

        if not table_exists:
            raise RuntimeError(
                f"Table {TABLE_SCHEMA}.{TABLE_NAME} does not exist."
            )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards;
            """
        )

        existing_cards = cursor.fetchone()[0]

        print(
            f"Existing Credit Cards : {existing_cards:,}"
        )

        if existing_cards > 0:
            raise RuntimeError(
                "Credit card table already contains data.\n"
                "The loader will NOT delete existing credit cards."
            )


# ============================================================
# READ CSV
# ============================================================

def read_csv() -> pd.DataFrame:

    print_header("READING CREDIT CARDS CSV")

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Credit cards CSV not found:\n{CSV_FILE}"
        )

    df = pd.read_csv(CSV_FILE)

    print("Credit Cards CSV Loaded Successfully")
    print(f"Total Records : {len(df):,}")

    return df


# ============================================================
# VALIDATE CSV STRUCTURE
# ============================================================

def validate_columns(df: pd.DataFrame) -> None:

    print_header("CSV COLUMN VALIDATION")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        print("ERROR: Missing required credit card columns:")

        for column in missing_columns:
            print(f" - {column}")

        raise RuntimeError(
            "Credit card CSV column validation failed."
        )

    print("Required CSV Columns Validation Passed")


# ============================================================
# NULL VALIDATION
# ============================================================

def validate_nulls(df: pd.DataFrame) -> None:

    print_header("NULL VALUE VALIDATION")

    required_non_null_columns = [
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

    null_values = (
        df[required_non_null_columns]
        .isnull()
        .sum()
        .sum()
    )

    print(
        f"NULL Values In Required Columns : {null_values:,}"
    )

    if null_values > 0:
        raise RuntimeError(
            "NULL values found in required columns."
        )

    print("No NULL values found in required columns.")


# ============================================================
# DUPLICATE VALIDATION
# ============================================================

def validate_duplicates(df: pd.DataFrame) -> None:

    print_header("DUPLICATE VALIDATION")

    duplicate_card_ids = (
        df["card_id"]
        .duplicated()
        .sum()
    )

    duplicate_card_numbers = (
        df["card_number"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate Card IDs : {duplicate_card_ids:,}"
    )

    print(
        f"Duplicate Card Numbers : "
        f"{duplicate_card_numbers:,}"
    )

    if duplicate_card_ids > 0:
        raise RuntimeError(
            "Duplicate card IDs found."
        )

    if duplicate_card_numbers > 0:
        raise RuntimeError(
            "Duplicate card numbers found."
        )


# ============================================================
# CARD ID VALIDATION
# ============================================================

def validate_card_ids(df: pd.DataFrame) -> None:

    print_header("CARD ID VALIDATION")

    invalid_card_ids = (
        pd.to_numeric(
            df["card_id"],
            errors="coerce"
        ).isnull()
    ).sum()

    non_positive_card_ids = (
        pd.to_numeric(
            df["card_id"],
            errors="coerce"
        ) <= 0
    ).sum()

    print(
        f"Invalid Card IDs : {invalid_card_ids:,}"
    )

    print(
        f"Non-positive Card IDs : "
        f"{non_positive_card_ids:,}"
    )

    if invalid_card_ids > 0:
        raise RuntimeError(
            "Invalid card IDs found."
        )

    if non_positive_card_ids > 0:
        raise RuntimeError(
            "Non-positive card IDs found."
        )


# ============================================================
# CARD NUMBER VALIDATION
# ============================================================

def validate_card_numbers(df: pd.DataFrame) -> None:

    print_header("CARD NUMBER VALIDATION")

    invalid_card_numbers = (
        ~df["card_number"]
        .astype(str)
        .str.fullmatch(r"\d{16}")
    ).sum()

    print(
        f"Invalid Card Numbers : "
        f"{invalid_card_numbers:,}"
    )

    if invalid_card_numbers > 0:
        raise RuntimeError(
            "Card numbers must contain exactly 16 digits."
        )


# ============================================================
# FINANCIAL VALIDATION
# ============================================================

def validate_financial_values(df: pd.DataFrame) -> None:

    print_header("FINANCIAL VALUE VALIDATION")

    invalid_credit_limits = (
        pd.to_numeric(
            df["credit_limit"],
            errors="coerce"
        ) <= 0
    ).sum()

    invalid_available_credit = (
        (
            pd.to_numeric(
                df["available_credit"],
                errors="coerce"
            ) < 0
        )
        |
        (
            pd.to_numeric(
                df["available_credit"],
                errors="coerce"
            )
            >
            pd.to_numeric(
                df["credit_limit"],
                errors="coerce"
            )
        )
    ).sum()

    invalid_outstanding_balance = (
        (
            pd.to_numeric(
                df["outstanding_balance"],
                errors="coerce"
            ) < 0
        )
        |
        (
            pd.to_numeric(
                df["outstanding_balance"],
                errors="coerce"
            )
            >
            pd.to_numeric(
                df["credit_limit"],
                errors="coerce"
            )
        )
    ).sum()

    balance_mismatch = (
        (
            pd.to_numeric(
                df["available_credit"],
                errors="coerce"
            )
            +
            pd.to_numeric(
                df["outstanding_balance"],
                errors="coerce"
            )
            -
            pd.to_numeric(
                df["credit_limit"],
                errors="coerce"
            )
        ).abs() > 0.01
    ).sum()

    print(
        f"Invalid Credit Limits : "
        f"{invalid_credit_limits:,}"
    )

    print(
        f"Invalid Available Credit : "
        f"{invalid_available_credit:,}"
    )

    print(
        f"Invalid Outstanding Balances : "
        f"{invalid_outstanding_balance:,}"
    )

    print(
        f"Balance Consistency Errors : "
        f"{balance_mismatch:,}"
    )

    if invalid_credit_limits > 0:
        raise RuntimeError(
            "Invalid credit limits found."
        )

    if invalid_available_credit > 0:
        raise RuntimeError(
            "Invalid available credit values found."
        )

    if invalid_outstanding_balance > 0:
        raise RuntimeError(
            "Invalid outstanding balances found."
        )

    if balance_mismatch > 0:
        raise RuntimeError(
            "Available credit + outstanding balance "
            "does not equal credit limit."
        )


# ============================================================
# DATE VALIDATION
# ============================================================

def validate_dates(df: pd.DataFrame) -> None:

    print_header("DATE VALIDATION")

    issue_dates = pd.to_datetime(
        df["issue_date"],
        errors="coerce"
    )

    expiry_dates = pd.to_datetime(
        df["expiry_date"],
        errors="coerce"
    )

    invalid_issue_dates = issue_dates.isnull().sum()

    invalid_expiry_dates = expiry_dates.isnull().sum()

    invalid_date_relationships = (
        expiry_dates <= issue_dates
    ).sum()

    print(
        f"Invalid Issue Dates : "
        f"{invalid_issue_dates:,}"
    )

    print(
        f"Invalid Expiry Dates : "
        f"{invalid_expiry_dates:,}"
    )

    print(
        f"Invalid Issue/Expiry Relationships : "
        f"{invalid_date_relationships:,}"
    )

    if invalid_issue_dates > 0:
        raise RuntimeError(
            "Invalid issue dates found."
        )

    if invalid_expiry_dates > 0:
        raise RuntimeError(
            "Invalid expiry dates found."
        )

    if invalid_date_relationships > 0:
        raise RuntimeError(
            "Expiry date must be later than issue date."
        )


# ============================================================
# LOAD CUSTOMER / ACCOUNT IDs FROM DATABASE
# ============================================================

def load_reference_ids(conn):

    print_header("LOADING REFERENCE DATA")

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT customer_id
            FROM public.customers;
            """
        )

        customer_ids = {
            row[0]
            for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT account_id, customer_id
            FROM public.accounts;
            """
        )

        account_relationships = {
            (row[0], row[1])
            for row in cursor.fetchall()
        }

    print(
        f"Customer IDs Available : "
        f"{len(customer_ids):,}"
    )

    print(
        f"Account / Customer Relationships : "
        f"{len(account_relationships):,}"
    )

    return customer_ids, account_relationships


# ============================================================
# FOREIGN KEY VALIDATION
# ============================================================

def validate_foreign_keys(
    df: pd.DataFrame,
    customer_ids: set,
    account_relationships: set,
) -> None:

    print_header("FOREIGN KEY VALIDATION")

    invalid_customer_ids = (
        ~df["customer_id"].isin(customer_ids)
    ).sum()

    invalid_account_relationships = 0

    for account_id, customer_id in zip(
        df["account_id"],
        df["customer_id"],
    ):
        if (
            account_id,
            customer_id
        ) not in account_relationships:
            invalid_account_relationships += 1

    print(
        f"Invalid Customer IDs : "
        f"{invalid_customer_ids:,}"
    )

    print(
        f"Invalid Account / Customer Relationships : "
        f"{invalid_account_relationships:,}"
    )

    if invalid_customer_ids > 0:
        raise RuntimeError(
            "Invalid customer references found."
        )

    if invalid_account_relationships > 0:
        raise RuntimeError(
            "Invalid account/customer relationships found."
        )

    print("Foreign Key Validation Passed")


# ============================================================
# VALIDATE RECORD COUNT
# ============================================================

def validate_record_count(df: pd.DataFrame) -> None:

    print_header("CREDIT CARD DATA VALIDATION")

    print(
        f"Expected CSV Records : "
        f"{EXPECTED_RECORDS:,}"
    )

    print(
        f"Actual CSV Records : "
        f"{len(df):,}"
    )

    if len(df) != EXPECTED_RECORDS:
        raise RuntimeError(
            "Unexpected number of credit card records."
        )


# ============================================================
# CHECK IDENTITY COLUMN
# ============================================================

def card_id_is_identity(conn) -> bool:

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT is_identity
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
              AND column_name = 'card_id';
            """,
            (TABLE_SCHEMA, TABLE_NAME),
        )

        result = cursor.fetchone()

        if result is None:
            raise RuntimeError(
                "card_id column was not found."
            )

        return result[0] == "YES"


# ============================================================
# LOAD DATA
# ============================================================

def load_data(conn, df: pd.DataFrame) -> None:

    print_header("LOADING CREDIT CARDS INTO POSTGRESQL")

    identity_column = card_id_is_identity(conn)

    columns = REQUIRED_COLUMNS

    column_sql = sql.SQL(", ").join(
        sql.Identifier(column)
        for column in columns
    )

    table_sql = sql.Identifier(
        TABLE_SCHEMA,
        TABLE_NAME
    )

    if identity_column:

        insert_sql = sql.SQL(
            """
            INSERT INTO {} ({})
            OVERRIDING SYSTEM VALUE
            VALUES %s
            """
        ).format(
            table_sql,
            column_sql
        )

    else:

        insert_sql = sql.SQL(
            """
            INSERT INTO {} ({})
            VALUES %s
            """
        ).format(
            table_sql,
            column_sql
        )

    records = list(
        df[columns].itertuples(
            index=False,
            name=None
        )
    )

    print(
        f"Records Prepared : {len(records):,}"
    )

    try:

        with conn.cursor() as cursor:

            for start in range(
                0,
                len(records),
                BATCH_SIZE
            ):

                batch = records[
                    start:start + BATCH_SIZE
                ]

                execute_values(
                    cursor,
                    insert_sql.as_string(conn),
                    batch,
                    page_size=BATCH_SIZE,
                )

                loaded = min(
                    start + len(batch),
                    len(records)
                )

                print(
                    f"Credit Cards Loaded : "
                    f"{loaded:,} / {len(records):,}"
                )

        conn.commit()

        print()
        print(
            "Credit Cards Inserted Successfully"
        )

    except Exception:

        conn.rollback()

        print()
        print(
            "ERROR WHILE LOADING CREDIT CARDS"
        )

        raise


# ============================================================
# SYNCHRONIZE CARD ID SEQUENCE
# ============================================================

def synchronize_card_id_sequence(conn) -> None:

    print_header("SYNCHRONIZING CARD ID SEQUENCE")

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT pg_get_serial_sequence(
                'public.credit_cards',
                'card_id'
            );
            """
        )

        sequence_name = cursor.fetchone()[0]

        if sequence_name:

            cursor.execute(
                """
                SELECT MAX(card_id)
                FROM public.credit_cards;
                """
            )

            max_card_id = cursor.fetchone()[0]

            if max_card_id is not None:

                cursor.execute(
                    """
                    SELECT setval(
                        pg_get_serial_sequence(
                            'public.credit_cards',
                            'card_id'
                        ),
                        %s,
                        true
                    );
                    """,
                    (max_card_id,),
                )

                conn.commit()

                print(
                    "Card Identity Sequence Synchronized"
                )

            else:

                print(
                    "No Card IDs Found - Sequence Not Updated"
                )

        else:

            print(
                "Card ID is not sequence-backed - "
                "no sequence update required."
            )


# ============================================================
# POST-LOAD VALIDATION
# ============================================================

def validate_loaded_data(
    conn,
    expected_count: int,
) -> None:

    print_header("CREDIT CARD LOAD VALIDATION")

    with conn.cursor() as cursor:

        # ----------------------------------------------------
        # Count
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards;
            """
        )

        database_count = cursor.fetchone()[0]

        print(
            f"Expected CSV Records : "
            f"{expected_count:,}"
        )

        print(
            f"Database Records : "
            f"{database_count:,}"
        )

        if database_count != expected_count:
            raise RuntimeError(
                "Database record count does not match CSV."
            )

        # ----------------------------------------------------
        # Duplicate Card IDs
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT card_id
                FROM public.credit_cards
                GROUP BY card_id
                HAVING COUNT(*) > 1
            ) duplicate_cards;
            """
        )

        duplicate_card_ids = cursor.fetchone()[0]

        print(
            f"Duplicate Card IDs : "
            f"{duplicate_card_ids:,}"
        )

        # ----------------------------------------------------
        # Duplicate Card Numbers
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT card_number
                FROM public.credit_cards
                GROUP BY card_number
                HAVING COUNT(*) > 1
            ) duplicate_numbers;
            """
        )

        duplicate_card_numbers = cursor.fetchone()[0]

        print(
            f"Duplicate Card Numbers : "
            f"{duplicate_card_numbers:,}"
        )

        # ----------------------------------------------------
        # Invalid Customer References
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards cc
            LEFT JOIN public.customers c
                ON cc.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
            """
        )

        invalid_customer_refs = cursor.fetchone()[0]

        print(
            f"Invalid Customer References : "
            f"{invalid_customer_refs:,}"
        )

        # ----------------------------------------------------
        # Invalid Account References
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards cc
            LEFT JOIN public.accounts a
                ON cc.account_id = a.account_id
            WHERE a.account_id IS NULL;
            """
        )

        invalid_account_refs = cursor.fetchone()[0]

        print(
            f"Invalid Account References : "
            f"{invalid_account_refs:,}"
        )

        # ----------------------------------------------------
        # Invalid Account / Customer Relationship
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards cc
            LEFT JOIN public.accounts a
                ON cc.account_id = a.account_id
               AND cc.customer_id = a.customer_id
            WHERE a.account_id IS NULL;
            """
        )

        invalid_relationships = cursor.fetchone()[0]

        print(
            f"Invalid Account / Customer Relationships : "
            f"{invalid_relationships:,}"
        )

        # ----------------------------------------------------
        # Invalid Financial Values
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards
            WHERE credit_limit <= 0
               OR available_credit < 0
               OR outstanding_balance < 0
               OR available_credit > credit_limit
               OR outstanding_balance > credit_limit;
            """
        )

        invalid_financial_values = cursor.fetchone()[0]

        print(
            f"Invalid Financial Records : "
            f"{invalid_financial_values:,}"
        )

        # ----------------------------------------------------
        # Balance consistency
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards
            WHERE ABS(
                available_credit
                + outstanding_balance
                - credit_limit
            ) > 0.01;
            """
        )

        balance_errors = cursor.fetchone()[0]

        print(
            f"Balance Consistency Errors : "
            f"{balance_errors:,}"
        )

        # ----------------------------------------------------
        # Invalid Dates
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM public.credit_cards
            WHERE expiry_date <= issue_date;
            """
        )

        invalid_dates = cursor.fetchone()[0]

        print(
            f"Invalid Issue / Expiry Dates : "
            f"{invalid_dates:,}"
        )

    if duplicate_card_ids > 0:
        raise RuntimeError(
            "Duplicate card IDs found after load."
        )

    if duplicate_card_numbers > 0:
        raise RuntimeError(
            "Duplicate card numbers found after load."
        )

    if invalid_customer_refs > 0:
        raise RuntimeError(
            "Invalid customer references found."
        )

    if invalid_account_refs > 0:
        raise RuntimeError(
            "Invalid account references found."
        )

    if invalid_relationships > 0:
        raise RuntimeError(
            "Invalid account/customer relationships found."
        )

    if invalid_financial_values > 0:
        raise RuntimeError(
            "Invalid financial records found."
        )

    if balance_errors > 0:
        raise RuntimeError(
            "Balance consistency validation failed."
        )

    if invalid_dates > 0:
        raise RuntimeError(
            "Invalid issue/expiry dates found."
        )

    print()
    print(
        "CREDIT CARD LOAD VALIDATION PASSED"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    conn = None

    try:

        conn = connect_database()

        validate_table(conn)

        df = read_csv()

        validate_record_count(df)

        validate_columns(df)

        validate_nulls(df)

        validate_duplicates(df)

        validate_card_ids(df)

        validate_card_numbers(df)

        validate_financial_values(df)

        validate_dates(df)

        customer_ids, account_relationships = (
            load_reference_ids(conn)
        )

        validate_foreign_keys(
            df,
            customer_ids,
            account_relationships,
        )

        print_header("CREDIT CARD DATA VALIDATION PASSED")

        load_data(
            conn,
            df,
        )

        synchronize_card_id_sequence(conn)

        validate_loaded_data(
            conn,
            len(df),
        )

        print_header("CREDIT CARDS LOADED SUCCESSFULLY")

        print()
        print(
            f"Credit Card Records Loaded : "
            f"{len(df):,}"
        )

        print()
        print(
            "Credit Card Load Process Completed"
        )

        print("=" * 65)

    except Exception as exc:

        print()
        print(
            "CREDIT CARD LOAD PROCESS FAILED"
        )

        print(
            f"ERROR: {exc}"
        )

        if conn:
            conn.rollback()

        raise SystemExit(1)

    finally:

        if conn:

            conn.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()