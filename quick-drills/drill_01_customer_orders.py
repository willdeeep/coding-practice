import sqlite3


def _seed(conn):
    conn.execute("CREATE TABLE orders (order_id INTEGER, customer_name TEXT, amount REAL)")
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?)",
        [(1, "Alice", 42.50), (2, "Bob", 19.99), (3, "Alice", 7.25)],
    )
    conn.commit()


def get_orders_for_customer(customer_name: str, conn: sqlite3.Connection):
    query = f"SELECT order_id, amount FROM orders WHERE customer_name = '{customer_name}'"
    return conn.execute(query).fetchall()


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    _seed(conn)
    print(get_orders_for_customer("Alice", conn))
    conn.close()
