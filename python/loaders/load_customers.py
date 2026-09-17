import pandas as pd
import psycopg2

# ---------------------------------------
# Connect to PostgreSQL
# ---------------------------------------

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

# ---------------------------------------
# Read Customers CSV
# ---------------------------------------

df = pd.read_csv("data/raw/customers.csv")

if df.empty:
    print("Customer CSV is empty.")
    exit()

print()
print("--------------------------------")
print("Customers CSV Loaded Successfully")
print("--------------------------------")
print()

print(df.head())

print()

print("Total Records :", len(df))

# ---------------------------------------
# INSERT Query
# ---------------------------------------

insert_query = """
INSERT INTO customers
(
    customer_id,
    customer_number,
    first_name,
    last_name,
    date_of_birth,
    gender,
    email,
    phone,
    ssn,
    address,
    city,
    state,
    zip_code,
    country,
    customer_since,
    occupation,
    annual_income,
    risk_rating,
    kyc_status,
    customer_status,
    branch_id
)
VALUES
(
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s
)
"""

# ---------------------------------------
# Load Customers into PostgreSQL
# ---------------------------------------


for _, row in df.iterrows():

    try:

        cursor.execute(
            insert_query,
            (
                row["customer_id"],
                row["customer_number"],
                row["first_name"],
                row["last_name"],
                row["date_of_birth"],
                row["gender"],
                row["email"],
                row["phone"],
                row["ssn"],
                row["address"],
                row["city"],
                row["state"],
                row["zip_code"],
                row["country"],
                row["customer_since"],
                row["occupation"],
                row["annual_income"],
                row["risk_rating"],
                row["kyc_status"],
                row["customer_status"],
                row["branch_id"]
            )
        )

  

    # ---------------------------------------
# Save Changes
# ---------------------------------------

conn.commit()

# ---------------------------------------
# Close Database Connection
# ---------------------------------------

cursor.close()
conn.close()

# ---------------------------------------
# Success Message
# ---------------------------------------

print()

print("--------------------------------")
print("Customers Loaded Successfully")
print("--------------------------------")

print()

print("Rows Loaded :", len(df))