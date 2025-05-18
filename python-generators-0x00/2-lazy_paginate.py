#!/usr/bin/python3
"""
Lazy pagination of user_data table using generators.
"""
import seed

def paginate_users(page_size, offset):
    """
    Fetch a page of users from the database starting at offset.
    Returns a list of dict rows.
    """
    conn = seed.connect_to_prodev()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s",
        (page_size, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that yields pages of users lazily.
    """
    offset = 0
    while True:  # single loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
