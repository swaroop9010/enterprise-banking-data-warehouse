from faker import Faker
import pandas as pd
import random

fake = Faker("en_US")

NUMBER_OF_BRANCHES = 1000

cities = [
    ("New York", "NY"),
    ("Los Angeles", "CA"),
    ("Chicago", "IL"),
    ("Houston", "TX"),
    ("Phoenix", "AZ"),
    ("Philadelphia", "PA"),
    ("San Antonio", "TX"),
    ("San Diego", "CA"),
    ("Dallas", "TX"),
    ("San Jose", "CA")
]

branches = []

for i in range(NUMBER_OF_BRANCHES):

    city, state = random.choice(cities)

    branch = {

        "branch_code": f"BR{str(i+1).zfill(4)}",

        "branch_name": f"{city} Branch",

        "address": fake.street_address(),

        "city": city,

        "state": state,

        "zip_code": fake.zipcode(),

        "country": "USA",

        "phone": fake.numerify("###-###-####"),

        "manager_name": fake.name(),

        "opening_date": fake.date_between(
            start_date="-20y",
            end_date="-1y"
        ),

        "branch_status": random.choice(
            ["Active", "Inactive"]
        )

    }

    branches.append(branch)

df = pd.DataFrame(branches)

df.to_csv(
    "data/raw/branches.csv",
    index=False
)

print(df.head())
print()
print("--------------------------------")
print("Branches Generated Successfully")
print("--------------------------------")
print()
print("Total Branches :", len(df))