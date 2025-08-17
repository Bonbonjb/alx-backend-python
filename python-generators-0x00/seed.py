import mysql.connector
import csv
import uuid


def connect_db():
    """Connect to MySQL server (no specific database)"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="your_username",      
            password="your_password"   
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


def create_database(connection):
    """Create ALX_prodev database if it doesn't exist"""
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()


def connect_to_prodev():
    """Connect to the ALX_prodev database"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="your_username",      
            password="your_password",   
            database="ALX_prodev"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None


def create_table(connection):
    """Create the user_data table if it doesn't exist"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL,
        INDEX idx_email (email)
    )
    """
    cursor = connection.cursor()
    cursor.execute(create_sql)
    connection.commit()
    cursor.close()
    print("Table user_data created successfully")


def insert_data(connection, csv_path):
    """Insert rows from CSV into the table, skipping duplicates by email"""
    cursor = connection.cursor()
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email']
            cursor.execute("SELECT 1 FROM user_data WHERE email = %s", (email,))
            if cursor.fetchone():
                continue
            user_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                (user_id, row['name'], email, row['age'])
            )
    connection.commit()
    cursor.close()


def stream_rows(connection, batch_size=1):
    """
    Generator that yields rows from user_data table one by one (or in batches).
    :param connection: MySQL connection to ALX_prodev
    :param batch_size: number of rows to fetch per batch
    """
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        for row in rows:
            yield row
    cursor.close()


if __name__ == "__main__":
    # Standalone test: seed database and stream first 5 rows
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()
        print("Database created/verified.")
        conn = connect_to_prodev()
        if conn:
            create_table(conn)
            insert_data(conn, 'user_data.csv')
            print("Data inserted.")
            # Stream rows
            gen = stream_rows(conn)
            print("First 5 rows streamed:")
            for _ in range(5):
                try:
                    print(next(gen))
                except StopIteration:
                    break
            conn.close()
