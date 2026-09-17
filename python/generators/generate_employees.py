from faker import Faker
import pandas as pd
import random
import psycopg2

# ---------------------------------------
# Faker
# ---------------------------------------

fake = Faker("en_US")

NUMBER_OF_EMPLOYEES = 5000

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

cursor.execute("""
SELECT branch_id
FROM branches
ORDER BY branch_id
""")

branch_ids = [row[0] for row in cursor.fetchall()]

cursor.close()
conn.close()

print(f"Total Branches Found : {len(branch_ids)}")

# ---------------------------------------
# Lookup Lists
# ---------------------------------------

job_titles = [
    "Branch Manager",
    "Assistant Manager",
    "Relationship Manager",
    "Loan Officer",
    "Credit Analyst",
    "Customer Service Representative",
    "Cashier",
    "Operations Officer",
    "Financial Advisor",
    "Teller"
]

departments = [
    "Retail Banking",
    "Loans",
    "Operations",
    "Customer Service",
    "Finance",
    "Compliance",
    "Risk Management",
    "Wealth Management"
]

# ---------------------------------------
# Generate Employees
# ---------------------------------------

employees = []

for i in range(NUMBER_OF_EMPLOYEES):

    first_name = fake.first_name()
    last_name = fake.last_name()

    employee = {

        "employee_number": f"EMP{str(i+1).zfill(5)}",

        "first_name": first_name,

        "last_name": last_name,

        "email": f"{first_name.lower()}.{last_name.lower()}{i}@bank.com",

        "phone": fake.numerify("###-###-####"),

        "job_title": random.choice(job_titles),

        "department": random.choice(departments),

        # Select an EXISTING branch_id
        "branch_id": random.choice(branch_ids),

        "hire_date": fake.date_between(
            start_date="-20y",
            end_date="today"
        ),

        "salary": round(
            random.uniform(35000, 180000),
            2
        ),

        "employment_status": random.choice(
            [
                "Active",
                "Inactive",
                "On Leave",
                "Terminated"
            ]
        )

    }

    employees.append(employee)

# ---------------------------------------
# Create DataFrame
# ---------------------------------------

df = pd.DataFrame(employees)

# ---------------------------------------
# Save CSV
# ---------------------------------------

df.to_csv(
    "data/raw/employees.csv",
    index=False
)

# ---------------------------------------
# Output
# ---------------------------------------

print(df.head())

print()
print("--------------------------------------")
print("Employees Generated Successfully")
print("--------------------------------------")
print()
print("Total Employees :", len(df))