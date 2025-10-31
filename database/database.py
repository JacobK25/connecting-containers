
import psycopg2


connection = psycopg2.connect(
    database="test_database",
    host="127.0.0.1",
    port="5432"
)

cursor = connection.cursor()

cursor.execute("SELECT * FROM DB_table WHERE id = 1")