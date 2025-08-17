#!/usr/bin/python3
"""
Memory-efficient aggregation: compute average age using generators.
"""
from seed import connect_to_prodev

def stream_user_ages():
    """
    Generator that yields each user's age from user_data table.
    """
    conn = connect_to_prodev()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM user_data")
    for (age,) in cursor:
        yield age
    cursor.close()
    conn.close()


def calculate_average_age():
    """
    Calculate and print the average age using the age stream generator.
    Uses only one loop over the generator.
    """
    total = 0
    count = 0
    for age in stream_user_ages():  # loop 1
        total += age
        count += 1
    if count:
        average = total / count
        print(f"Average age of users: {average}")
    else:
        print("No user data found.")

if __name__ == "__main__":
    calculate_average_age()
