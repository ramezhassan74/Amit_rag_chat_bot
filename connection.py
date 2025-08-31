import psycopg

conn = psycopg.connect(
    dbname="mydb",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

