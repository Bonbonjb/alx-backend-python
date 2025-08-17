#!/usr/bin/python3
"""
Generator that streams rows from the user_data table one by one using yield.
"""
import mysql.connector
from seed import connect_to_prodev

def stream_users():
    """
    Connects to ALX_prodev and yields each user record as a dict.
    """
    conn = connect_to_prodev()
    if conn is None:
        return
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    for row in cursor:
        yield row
    cursor.close()
    conn.close()
