import sqlite3


def _seed(conn):
    conn.execute("CREATE TABLE products (sku TEXT, name TEXT, price REAL)")
    conn.executemany(
        "INSERT INTO products VALUES (?, ?, ?)",
        [("A1", "Widget", 9.99), ("B2", "Gadget", 14.50), ("C3", "Gizmo", 3.75)],
    )
    conn.commit()


def get_prices(skus: list[str], conn: sqlite3.Connection) -> dict[str, float]:
    prices = {}
    for sku in skus:
        row = conn.execute("SELECT price FROM products WHERE sku = ?", (sku,)).fetchone()
        prices[sku] = row[0] if row else None
    return prices


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    _seed(conn)
    print(get_prices(["A1", "B2", "C3"], conn))
    conn.close()
