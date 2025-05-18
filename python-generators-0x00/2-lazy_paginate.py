#!/usr/bin/python3
"""
Lazy loading Paginated Data: fetch paginated batches of users lazily using generators.
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
        "SELECT * FROM user_data LIMIT %s OFFSET %s",
        (page_size, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def lazypaginate(page_size):
    """
    Generator that yields pages (lists) of users lazily, fetching only when needed at an offset starting at 0.

    Prototype:
        def lazypaginate(page_size)
    """
    offset = 0
    while True:  # only loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size



