import sqlite3


def _seed(conn):
    conn.execute("CREATE TABLE invoices (customer_id INTEGER, amount REAL)")
    conn.execute("CREATE TABLE payments (customer_id INTEGER, amount REAL)")
    conn.executemany("INSERT INTO invoices VALUES (?, ?)", [(1, 100.0), (1, 50.0), (2, 200.0)])
    conn.executemany(
        "INSERT INTO payments VALUES (?, ?)", [(1, 30.0), (1, 20.0), (1, 40.0), (2, 200.0)]
    )
    conn.commit()


def invoice_vs_paid(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT i.customer_id, SUM(i.amount) AS invoiced, SUM(p.amount) AS paid
        FROM invoices i
        JOIN payments p ON p.customer_id = i.customer_id
        GROUP BY i.customer_id
        """
    ).fetchall()


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    _seed(conn)
    print(invoice_vs_paid(conn))
    conn.close()
