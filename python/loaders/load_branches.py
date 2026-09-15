import pandas as pd
import psycopg2

# -----------------------------
# Read CSV
# -----------------------------
df = pd.read_csv("data/raw/branches.csv")

# -----------------------------
# Connect to PostgreSQL
# -----------------------------
conn = psycopg2.connect(
    host="localhost",
    database="enterprisebankingdw",
    user="postgres",
    password="1976",          # <-- change if your password is different
    port="5432"
)

cursor = conn.cursor()

# -----------------------------
# Insert Query
# -----------------------------
insert_query = """
INSERT INTO branches
(
    branch_code,
    branch_name,
    address,
    city,
    state,
    zip_code,
    country,
    phone,
    manager_name,
    opening_date,
    branch_status
)
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
    %s
)
"""

# -----------------------------
# Load Data
# -----------------------------
for _, row in df.iterrows():

    cursor.execute(
        insert_query,
        (
            row["branch_code"],
            row["branch_name"],
            row["address"],
            row["city"],
            row["state"],
            row["zip_code"],
            row["country"],
            row["phone"],
            row["manager_name"],
            row["opening_date"],
            row["branch_status"]
        )
    )

# -----------------------------
# Commit
# -----------------------------
conn.commit()

print("-------------------------------------")
print("Branches Loaded Successfully")
print("-------------------------------------")
print()
print("Rows Loaded :", len(df))

cursor.close()
conn.close()