import sqlite3


def _seed(conn):
    conn.execute("CREATE TABLE orders (order_id INTEGER, order_date TEXT)")
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?)",
        [(1, "2024-11-03"), (2, "2025-01-15"), (3, "2025-06-30")],
    )
    conn.commit()


def orders_in_year(year: str, conn: sqlite3.Connection):
    return conn.execute(
        "SELECT order_id, order_date FROM orders WHERE strftime('%Y', order_date) = ?",
        (year,),
    ).fetchall()


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    _seed(conn)
    print(orders_in_year("2025", conn))
    conn.close()
