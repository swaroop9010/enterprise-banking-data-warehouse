from faker import Faker
import pandas as pd
import random
import psycopg2

fake = Faker("en_US")

# ----------------------------------
# Read Branch IDs from PostgreSQL
# ----------------------------------

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

print("Branches Found :", len(branch_ids))

NUMBER_OF_CUSTOMERS = 50000

# ----------------------------------
# ID Counters
# ----------------------------------

customer_id = 1
customer_number = 1

customers = []

for i in range(NUMBER_OF_CUSTOMERS):

    first_name = fake.first_name()

    last_name = fake.last_name()

    customer = {

        "customer_id": customer_id,

        "customer_number": f"CUST{customer_number:06d}",

        "first_name": first_name,

        "last_name": last_name,

        "date_of_birth": fake.date_of_birth(
            minimum_age=18,
            maximum_age=80
        ),

        "gender": random.choice(
            ["Male", "Female"]
        ),

        "email": fake.unique.email(),

        "phone": fake.numerify(text="##########"),

        "ssn": fake.unique.ssn(),

        "address": fake.street_address(),

        "city": fake.city(),

        "state": fake.state(),

        "zip_code": fake.zipcode(),

        "country": "USA",

        "customer_since": fake.date_between(
            start_date="-10y",
            end_date="today"
        ),

        "occupation": fake.job(),

        "annual_income": random.randint(
            30000,
            250000
        ),

        "risk_rating": random.choice(
            ["Low","Medium","High"]
        ),

        "kyc_status": random.choice(
            ["Verified","Pending"]
        ),

        "customer_status": random.choice(
            ["Active","Inactive"]
        ),

        "branch_id": random.choice(branch_ids)

    }

    customers.append(customer)

    customer_id += 1
    customer_number += 1


df = pd.DataFrame(customers)

df.to_csv(
    "data/raw/customers.csv",
    index=False
)

print(df.head())

print()

print("--------------------------------")

print("Customers Generated Successfully")

print("--------------------------------")

print()

print("Total Customers :", len(df))