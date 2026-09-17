import pandas as pd
import psycopg2

# --------------------------
# Read CSV
# --------------------------

df = pd.read_csv("data/raw/employees.csv")

# --------------------------
# PostgreSQL Connection
# --------------------------

conn = psycopg2.connect(
    host="localhost",
    database="enterprisebankingdw",
    user="postgres",
    password="1976",
    port="5432"
)

cursor = conn.cursor()

# --------------------------
# Insert Query
# --------------------------

insert_query = """
INSERT INTO employees
(
    employee_number,
    first_name,
    last_name,
    email,
    phone,
    job_title,
    department,
    branch_id,
    hire_date,
    salary,
    employment_status
)
VALUES
(
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
)
"""

# --------------------------
# Load Records
# --------------------------

for _, row in df.iterrows():

    cursor.execute(
        insert_query,
        (
            row["employee_number"],
            row["first_name"],
            row["last_name"],
            row["email"],
            row["phone"],
            row["job_title"],
            row["department"],
            int(row["branch_id"]),
            row["hire_date"],
            float(row["salary"]),
            row["employment_status"]
        )
    )

# --------------------------
# Commit
# --------------------------

conn.commit()

print("-------------------------------------")
print("Employees Loaded Successfully")
print("-------------------------------------")
print()
print("Rows Loaded :", len(df))

cursor.close()
conn.close()