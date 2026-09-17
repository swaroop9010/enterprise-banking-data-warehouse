"""
load_loans.py

Enterprise Banking Data Warehouse
Loads loans.csv into PostgreSQL loans table.
"""

import csv
import getpass
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = Path("data/raw/loans.csv")

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "enterprisebankingdw"
DB_USER = "postgres"

TABLE_NAME = "loans"

BATCH_SIZE = 5000


# ============================================================
# LOAN TABLE COLUMNS
# Must match PostgreSQL loans table
# ============================================================

LOAN_COLUMNS = [
    "loan_id",
    "loan_number",
    "customer_id",
    "branch_id",
    "loan_type",
    "loan_amount",
    "outstanding_balance",
    "interest_rate",
    "loan_term_months",
    "monthly_payment",
    "start_date",
    "maturity_date",
    "loan_status",
    "created_at",
    "updated_at",
]


REQUIRED_CSV_COLUMNS = [
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
]


VALID_LOAN_TYPES = {
    "Personal",
    "Auto",
    "Mortgage",
    "Business",
    "Student",
}


VALID_LOAN_STATUSES = {
    "Active",
    "Approved",
    "Defaulted",
    "Paid Off",
    "Pending",
    "Rejected",
}


# ============================================================
# HELPER
# ============================================================

def print_section(title):
    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database():
    print_section("CONNECTING TO POSTGRESQL")

    password = getpass.getpass("Enter PostgreSQL password: ")

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=password,
        )

        print("Database Connected Successfully")

        return conn

    except Exception as exc:

        print()
        print("ERROR: Unable to connect to PostgreSQL")
        print("DETAIL:", exc)

        raise SystemExit(1)


# ============================================================
# CHECK TABLE EXISTS
# ============================================================

def validate_table(conn):

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = %s
            );
            """,
            (TABLE_NAME,),
        )

        table_exists = cursor.fetchone()[0]


    if not table_exists:

        print()
        print("ERROR: loans table does not exist.")

        raise SystemExit(1)

    print("Loans Table Found")


# ============================================================
# GET EXISTING RECORD COUNT
# ============================================================

def get_existing_count(conn):

    with conn.cursor() as cursor:

        cursor.execute(
            f"SELECT COUNT(*) FROM {TABLE_NAME};"
        )

        count = cursor.fetchone()[0]

    return count


# ============================================================
# READ CSV
# ============================================================

def read_csv():

    print_section("READING LOANS CSV")

    if not CSV_FILE.exists():

        print()
        print("ERROR: Loans CSV file not found.")
        print("File:", CSV_FILE)

        raise SystemExit(1)


    rows = []

    try:

        with CSV_FILE.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            csv_columns = reader.fieldnames or []


            # ------------------------------------------------
            # CSV COLUMN VALIDATION
            # ------------------------------------------------

            missing_columns = [
                column
                for column in REQUIRED_CSV_COLUMNS
                if column not in csv_columns
            ]


            if missing_columns:

                print()
                print(
                    "ERROR: Missing required CSV columns:"
                )

                for column in missing_columns:
                    print(" -", column)

                print()
                print("Available columns:")
                print(csv_columns)

                raise SystemExit(1)


            print(
                "Loans CSV Loaded Successfully"
            )

            row_number = 0


            for raw_row in reader:

                row_number += 1

                try:

                    loan_id = int(
                        raw_row["loan_id"]
                    )

                    loan_number = (
                        raw_row["loan_number"]
                    )

                    customer_id = int(
                        raw_row["customer_id"]
                    )

                    branch_id = int(
                        raw_row["branch_id"]
                    )

                    loan_type = (
                        raw_row["loan_type"]
                    )

                    loan_amount = float(
                        raw_row["loan_amount"]
                    )

                    outstanding_balance = float(
                        raw_row[
                            "outstanding_balance"
                        ]
                    )

                    interest_rate = float(
                        raw_row["interest_rate"]
                    )

                    loan_term_months = int(
                        raw_row[
                            "loan_term_months"
                        ]
                    )

                    monthly_payment = (
                        raw_row.get(
                            "monthly_payment"
                        )
                        or None
                    )

                    if monthly_payment is not None:

                        monthly_payment = float(
                            monthly_payment
                        )


                    start_date = (
                        raw_row["start_date"]
                    )

                    maturity_date = (
                        raw_row["maturity_date"]
                    )

                    loan_status = (
                        raw_row.get(
                            "loan_status"
                        )
                        or None
                    )

                    created_at = (
                        raw_row.get(
                            "created_at"
                        )
                        or None
                    )

                    updated_at = (
                        raw_row.get(
                            "updated_at"
                        )
                        or None
                    )


                    rows.append(
                        (
                            loan_id,
                            loan_number,
                            customer_id,
                            branch_id,
                            loan_type,
                            loan_amount,
                            outstanding_balance,
                            interest_rate,
                            loan_term_months,
                            monthly_payment,
                            start_date,
                            maturity_date,
                            loan_status,
                            created_at,
                            updated_at,
                        )
                    )

                except Exception as exc:

                    print()
                    print(
                        "ERROR: Invalid CSV row:",
                        row_number,
                    )

                    print(
                        "DETAIL:",
                        exc,
                    )

                    raise SystemExit(1)


    except SystemExit:
        raise

    except Exception as exc:

        print()
        print("ERROR: Unable to read loans CSV")
        print("DETAIL:", exc)

        raise SystemExit(1)


    print(
        "Total Records :",
        f"{len(rows):,}",
    )


    return rows


# ============================================================
# VALIDATE CSV DATA
# ============================================================

def validate_data(rows):

    print_section("LOAN DATA VALIDATION")

    validation_passed = True


    # --------------------------------------------------------
    # TOTAL RECORDS
    # --------------------------------------------------------

    print(
        "Total Loans :",
        f"{len(rows):,}",
    )


    if len(rows) != 500000:

        print(
            "ERROR: Expected 500,000 loan records."
        )

        validation_passed = False


    # --------------------------------------------------------
    # REQUIRED VALUES
    # --------------------------------------------------------

    required_null_count = 0


    for row in rows:

        for index in range(
            len(REQUIRED_CSV_COLUMNS)
        ):

            value = row[index]

            if value is None:

                required_null_count += 1


    print(
        "NULL Values In Required Columns :",
        required_null_count,
    )


    if required_null_count > 0:

        validation_passed = False


    # --------------------------------------------------------
    # DUPLICATE LOAN IDS
    # --------------------------------------------------------

    loan_ids = [
        row[0]
        for row in rows
    ]

    duplicate_loan_ids = (
        len(loan_ids)
        -
        len(set(loan_ids))
    )


    print(
        "Duplicate Loan IDs :",
        duplicate_loan_ids,
    )


    if duplicate_loan_ids > 0:

        validation_passed = False


    # --------------------------------------------------------
    # DUPLICATE LOAN NUMBERS
    # --------------------------------------------------------

    loan_numbers = [
        row[1]
        for row in rows
    ]

    duplicate_loan_numbers = (
        len(loan_numbers)
        -
        len(set(loan_numbers))
    )


    print(
        "Duplicate Loan Numbers :",
        duplicate_loan_numbers,
    )


    if duplicate_loan_numbers > 0:

        validation_passed = False


    # --------------------------------------------------------
    # INVALID LOAN TYPES
    # --------------------------------------------------------

    invalid_loan_types = sum(
        1
        for row in rows
        if row[4] not in VALID_LOAN_TYPES
    )


    print(
        "Invalid Loan Types :",
        invalid_loan_types,
    )


    if invalid_loan_types > 0:

        validation_passed = False


    # --------------------------------------------------------
    # INVALID LOAN STATUS
    # --------------------------------------------------------

    invalid_loan_statuses = sum(
        1
        for row in rows
        if row[12] is not None
        and row[12] not in VALID_LOAN_STATUSES
    )


    print(
        "Invalid Loan Statuses :",
        invalid_loan_statuses,
    )


    if invalid_loan_statuses > 0:

        validation_passed = False


    # --------------------------------------------------------
    # INVALID LOAN AMOUNTS
    # --------------------------------------------------------

    invalid_loan_amounts = sum(
        1
        for row in rows
        if row[5] <= 0
    )


    print(
        "Invalid Loan Amounts :",
        invalid_loan_amounts,
    )


    if invalid_loan_amounts > 0:

        validation_passed = False


    # --------------------------------------------------------
    # INVALID OUTSTANDING BALANCES
    # --------------------------------------------------------

    invalid_outstanding_balances = sum(
        1
        for row in rows
        if (
            row[6] < 0
            or row[6] > row[5]
        )
    )


    print(
        "Invalid Outstanding Balances :",
        invalid_outstanding_balances,
    )


    if invalid_outstanding_balances > 0:

        validation_passed = False


    # --------------------------------------------------------
    # INVALID INTEREST RATES
    # --------------------------------------------------------

    invalid_interest_rates = sum(
        1
        for row in rows
        if row[7] < 0
    )


    print(
        "Invalid Interest Rates :",
        invalid_interest_rates,
    )


    if invalid_interest_rates > 0:

        validation_passed = False


    # --------------------------------------------------------
    # INVALID LOAN TERMS
    # --------------------------------------------------------

    invalid_terms = sum(
        1
        for row in rows
        if row[8] <= 0
    )


    print(
        "Invalid Loan Terms :",
        invalid_terms,
    )


    if invalid_terms > 0:

        validation_passed = False


    # --------------------------------------------------------
    # MATURITY DATE CHECK
    # --------------------------------------------------------

    from datetime import datetime

    invalid_maturity_dates = 0


    for row in rows:

        try:

            start_date = datetime.fromisoformat(
                str(row[10])
            )

            maturity_date = datetime.fromisoformat(
                str(row[11])
            )

            if maturity_date <= start_date:

                invalid_maturity_dates += 1

        except Exception:

            invalid_maturity_dates += 1


    print(
        "Invalid Maturity Dates :",
        invalid_maturity_dates,
    )


    if invalid_maturity_dates > 0:

        validation_passed = False


    # --------------------------------------------------------
    # FINAL VALIDATION RESULT
    # --------------------------------------------------------

    if not validation_passed:

        print()
        print(
            "=" * 65
        )

        print(
            "LOAN DATA VALIDATION FAILED"
        )

        print(
            "=" * 65
        )

        raise SystemExit(1)


    print()
    print(
        "LOAN DATA VALIDATION PASSED"
    )


# ============================================================
# FOREIGN KEY VALIDATION
#
# Your loans table has branch_id -> branches.branch_id.
# We also validate customer_id against customers table when
# the column exists in that table.
# ============================================================

def validate_foreign_keys(conn, rows):

    print_section("FOREIGN KEY VALIDATION")


    # --------------------------------------------------------
    # BRANCH IDs
    # --------------------------------------------------------

    branch_ids = {
        row[3]
        for row in rows
    }


    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT branch_id
            FROM branches
            WHERE branch_id = ANY(%s);
            """,
            (list(branch_ids),),
        )

        valid_branch_ids = {
            row[0]
            for row in cursor.fetchall()
        }


    invalid_branch_ids = (
        branch_ids
        -
        valid_branch_ids
    )


    print(
        "Invalid Branch IDs :",
        len(invalid_branch_ids),
    )


    if invalid_branch_ids:

        print()
        print(
            "ERROR: Invalid branch IDs found."
        )

        raise SystemExit(1)


    # --------------------------------------------------------
    # CUSTOMER IDs
    # --------------------------------------------------------

    customer_ids = {
        row[2]
        for row in rows
    }


    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT customer_id
            FROM customers
            WHERE customer_id = ANY(%s);
            """,
            (list(customer_ids),),
        )

        valid_customer_ids = {
            row[0]
            for row in cursor.fetchall()
        }


    invalid_customer_ids = (
        customer_ids
        -
        valid_customer_ids
    )


    print(
        "Invalid Customer IDs :",
        len(invalid_customer_ids),
    )


    if invalid_customer_ids:

        print()
        print(
            "ERROR: Invalid customer IDs found."
        )

        raise SystemExit(1)


    print(
        "Foreign Key Validation Passed"
    )


# ============================================================
# LOAD DATA
# ============================================================

def load_data(conn, rows):

    print_section(
        "LOADING LOANS INTO POSTGRESQL"
    )


    insert_sql = f"""
    INSERT INTO {TABLE_NAME}
    (
        loan_id,
        loan_number,
        customer_id,
        branch_id,
        loan_type,
        loan_amount,
        outstanding_balance,
        interest_rate,
        loan_term_months,
        monthly_payment,
        start_date,
        maturity_date,
        loan_status,
        created_at,
        updated_at
    )
    OVERRIDING SYSTEM VALUE
    VALUES %s
"""


    try:

        with conn.cursor() as cursor:

            total_rows = len(rows)


            for start in range(
                0,
                total_rows,
                BATCH_SIZE
            ):

                batch = rows[
                    start:
                    start + BATCH_SIZE
                ]


                execute_values(
                    cursor,
                    insert_sql,
                    batch,
                    page_size=BATCH_SIZE,
                )


                processed = min(
                    start + BATCH_SIZE,
                    total_rows,
                )


                print(
                    f"Loans Loaded : "
                    f"{processed:,} / "
                    f"{total_rows:,}"
                )


        conn.commit()


        print()
        print(
            "LOANS LOADED SUCCESSFULLY"
        )


    except Exception as exc:

        conn.rollback()

        print()
        print(
            "ERROR WHILE LOADING LOANS"
        )

        print(
            "DETAIL:",
            exc,
        )

        print()
        print(
            "Transaction rolled back."
        )

        raise SystemExit(1)


# ============================================================
# SEQUENCE SYNCHRONIZATION
# ============================================================

def synchronize_sequence(conn):

    print_section(
        "SYNCHRONIZING LOAN ID SEQUENCE"
    )


    try:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT setval(
                    pg_get_serial_sequence(
                        'loans',
                        'loan_id'
                    ),
                    COALESCE(
                        (
                            SELECT MAX(loan_id)
                            FROM loans
                        ),
                        1
                    ),
                    true
                );
                """
            )


        conn.commit()


        print(
            "Loan Identity Sequence Synchronized"
        )


    except Exception as exc:

        conn.rollback()

        print()
        print(
            "WARNING: Could not synchronize "
            "loan_id sequence."
        )

        print(
            "DETAIL:",
            exc,
        )


# ============================================================
# FINAL DATABASE VALIDATION
# ============================================================

def final_validation(conn, expected_count):

    print_section(
        "LOAN LOAD VALIDATION"
    )


    with conn.cursor() as cursor:

        # ----------------------------------------------------
        # DATABASE COUNT
        # ----------------------------------------------------

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {TABLE_NAME};
            """
        )

        database_count = cursor.fetchone()[0]


        # ----------------------------------------------------
        # DUPLICATE LOAN IDs
        # ----------------------------------------------------

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT loan_id
                FROM {TABLE_NAME}
                GROUP BY loan_id
                HAVING COUNT(*) > 1
            ) x;
            """
        )

        duplicate_ids = cursor.fetchone()[0]


        # ----------------------------------------------------
        # DUPLICATE LOAN NUMBERS
        # ----------------------------------------------------

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT loan_number
                FROM {TABLE_NAME}
                GROUP BY loan_number
                HAVING COUNT(*) > 1
            ) x;
            """
        )

        duplicate_numbers = (
            cursor.fetchone()[0]
        )


        # ----------------------------------------------------
        # INVALID BRANCH REFERENCES
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM loans l
            LEFT JOIN branches b
                ON l.branch_id = b.branch_id
            WHERE b.branch_id IS NULL;
            """
        )

        invalid_branch_references = (
            cursor.fetchone()[0]
        )


        # ----------------------------------------------------
        # INVALID CUSTOMER REFERENCES
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM loans l
            LEFT JOIN customers c
                ON l.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
            """
        )

        invalid_customer_references = (
            cursor.fetchone()[0]
        )


        # ----------------------------------------------------
        # INVALID OUTSTANDING BALANCES
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM loans
            WHERE outstanding_balance < 0
               OR outstanding_balance > loan_amount;
            """
        )

        invalid_balances = (
            cursor.fetchone()[0]
        )


    print(
        "Expected CSV Records :",
        f"{expected_count:,}",
    )

    print(
        "Database Records :",
        f"{database_count:,}",
    )

    print(
        "Duplicate Loan IDs :",
        duplicate_ids,
    )

    print(
        "Duplicate Loan Numbers :",
        duplicate_numbers,
    )

    print(
        "Invalid Branch References :",
        invalid_branch_references,
    )

    print(
        "Invalid Customer References :",
        invalid_customer_references,
    )

    print(
        "Invalid Outstanding Balances :",
        invalid_balances,
    )


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    if (
        database_count != expected_count
        or duplicate_ids > 0
        or duplicate_numbers > 0
        or invalid_branch_references > 0
        or invalid_customer_references > 0
        or invalid_balances > 0
    ):

        print()
        print(
            "=" * 65
        )

        print(
            "LOAN LOAD VALIDATION FAILED"
        )

        print(
            "=" * 65
        )

        raise SystemExit(1)


    print()
    print(
        "LOAN LOAD VALIDATION PASSED"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=" * 65
    )

    print(
        "ENTERPRISE BANKING DW - LOAN LOAD"
    )

    print(
        "=" * 65
    )


    conn = None


    try:

        # ----------------------------------------------------
        # CONNECT
        # ----------------------------------------------------

        conn = connect_database()


        # ----------------------------------------------------
        # TABLE CHECK
        # ----------------------------------------------------

        validate_table(conn)


        # ----------------------------------------------------
        # EXISTING DATA
        # ----------------------------------------------------

        existing_count = get_existing_count(
            conn
        )


        print()
        print(
            "Existing Loans :",
            f"{existing_count:,}",
        )


        if existing_count > 0:

            print()
            print(
                "WARNING: Loans table already "
                "contains data."
            )

            print(
                "The loader will NOT delete "
                "existing loans."
            )

            print(
                "Stop here if you want a fresh load."
            )

            raise SystemExit(1)


        # ----------------------------------------------------
        # READ CSV
        # ----------------------------------------------------

        rows = read_csv()


        # ----------------------------------------------------
        # VALIDATE CSV
        # ----------------------------------------------------

        validate_data(rows)


        # ----------------------------------------------------
        # FOREIGN KEY VALIDATION
        # ----------------------------------------------------

        validate_foreign_keys(
            conn,
            rows,
        )


        # ----------------------------------------------------
        # LOAD
        # ----------------------------------------------------

        load_data(
            conn,
            rows,
        )


        # ----------------------------------------------------
        # SEQUENCE
        # ----------------------------------------------------

        synchronize_sequence(
            conn
        )


        # ----------------------------------------------------
        # FINAL VALIDATION
        # ----------------------------------------------------

        final_validation(
            conn,
            len(rows),
        )


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        print()
        print(
            "=" * 65
        )

        print(
            "LOANS LOADED SUCCESSFULLY"
        )

        print(
            "=" * 65
        )

        print()
        print(
            "Loan Load Process Completed"
        )

        print(
            "=" * 65
        )


    except SystemExit:
        raise


    except KeyboardInterrupt:

        print()
        print(
            "Loan load interrupted by user."
        )

        if conn:
            conn.rollback()

        raise SystemExit(1)


    except Exception as exc:

        if conn:
            conn.rollback()

        print()
        print(
            "=" * 65
        )

        print(
            "UNEXPECTED ERROR"
        )

        print(
            "=" * 65
        )

        print(
            "DETAIL:",
            exc,
        )

        raise SystemExit(1)


    finally:

        if conn:

            conn.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()