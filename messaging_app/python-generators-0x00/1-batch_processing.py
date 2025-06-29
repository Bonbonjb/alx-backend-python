#!/usr/bin/python3
"""
Batch processing of users from the user_data table using generators.
"""
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Generator that yields lists of user dicts in chunks of batch_size.
    """
    conn = connect_to_prodev()
    if conn is None:
        return
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch
    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """
    Processes batches of users, printing only those over age 25.
    """
    for batch in stream_users_in_batches(batch_size):  # loop 1
        for user in batch:                              # loop 2
            if user.get('age', 0) > 25:
                print(user)
                print()  # blank line between records
