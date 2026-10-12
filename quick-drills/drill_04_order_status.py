import os
import sqlite3
import tempfile


def _seed(conn):
    conn.execute("CREATE TABLE orders (order_id INTEGER, status TEXT)")
    conn.executemany("INSERT INTO orders VALUES (?, ?)", [(1, "shipped"), (2, "pending")])
    conn.commit()


def get_status(order_id: int, db_path: str) -> str | None:
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    return row[0] if row else None


if __name__ == "__main__":
    path = tempfile.mktemp(suffix=".db")
    conn = sqlite3.connect(path)
    _seed(conn)
    conn.close()

    print(get_status(1, path))
    print(get_status(2, path))
    os.remove(path)
