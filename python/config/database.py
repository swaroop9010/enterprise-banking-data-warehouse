import psycopg2

connection = psycopg2.connect(
    host="localhost",
    database="enterprisebankingdw",
    user="postgres",
    password="1976",
    port="5432"
)

print("Database Connected Successfully")