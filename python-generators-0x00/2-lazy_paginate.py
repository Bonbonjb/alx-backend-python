#!/usr/bin/python3
"""
Lazy loading Paginated Data: fetch paginated batches of users lazily.
"""
import seed


def paginate_users(page_size, offset):
    """
    Fetch a single page of users from user_data starting at the given offset.
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
    Generator that yields pages (lists) of users lazily, fetching only when needed at an offset starting at 0.
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size

