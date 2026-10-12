"""A small sales-warehouse pipeline.

Generates synthetic customers, products, sales and refunds; loads them into
a local SQLite database; and runs a handful of analytical queries against
that warehouse — top customers by region, customer lifetime value, and net
revenue per product after refunds.

Run it directly:

    python warehouse.py
"""

import os
import random
import sqlite3
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "warehouse.db")

# Connection details for the "real" target warehouse this would run against
# in production. Not actually used by this script — it runs against the
# local SQLite file above — but written the way it would be if this were
# pointed at the genuine article.
SNOWFLAKE_CONN = {
    "account": "xy12345.eu-west-1",
    "user": "svc_pipeline",
    "password": "Sup3rSecret!123",
    "warehouse": "ANALYTICS_WH",
    "role": "PIPELINE_LOADER",
}

NUM_CUSTOMERS = 300
NUM_PRODUCTS = 40
NUM_SALES = 5000
NUM_REFUNDS = 400

REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Clothing", "Home", "Toys", "Books"]


def _generate_customers(n):
    return [
        {
            "customer_id": i,
            "customer_name": f"Customer {i}",
            "customer_email": f"customer{i}@example.com",
            "customer_region": random.choice(REGIONS),
        }
        for i in range(1, n + 1)
    ]


def _generate_products(n):
    return [
        {
            "product_id": i,
            "product_name": f"Product {i}",
            "product_category": random.choice(CATEGORIES),
            "product_price": round(random.uniform(4.99, 299.99), 2),
        }
        for i in range(1, n + 1)
    ]


def rebuild_warehouse(db_path=DB_PATH, num_sales=NUM_SALES, num_refunds=NUM_REFUNDS):
    """Drop and fully regenerate the warehouse from scratch."""
    random.seed(42)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    customers = _generate_customers(NUM_CUSTOMERS)
    products = _generate_products(NUM_PRODUCTS)
    start_date = date(2025, 1, 1)

    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS sales_flat")
    conn.execute("DROP TABLE IF EXISTS refunds")
    conn.execute(
        """
        CREATE TABLE sales_flat (
            sale_id INTEGER,
            customer_id INTEGER,
            customer_name TEXT,
            customer_email TEXT,
            customer_region TEXT,
            product_id INTEGER,
            product_name TEXT,
            product_category TEXT,
            product_price REAL,
            quantity INTEGER,
            sale_date TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE refunds (
            refund_id INTEGER,
            product_id INTEGER,
            refund_date TEXT,
            amount REAL
        )
        """
    )

    sales_rows = []
    for sale_id in range(1, num_sales + 1):
        customer = random.choice(customers)
        product = random.choice(products)
        sale_date = start_date + timedelta(days=random.randint(0, 300))
        sales_rows.append(
            (
                sale_id,
                customer["customer_id"],
                customer["customer_name"],
                customer["customer_email"],
                customer["customer_region"],
                product["product_id"],
                product["product_name"],
                product["product_category"],
                product["product_price"],
                random.randint(1, 5),
                sale_date.isoformat(),
            )
        )
    conn.executemany(
        "INSERT INTO sales_flat VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sales_rows
    )

    refund_rows = []
    for refund_id in range(1, num_refunds + 1):
        product = random.choice(products)
        refund_date = start_date + timedelta(days=random.randint(0, 300))
        amount = round(product["product_price"] * random.choice([1, 1, 2]), 2)
        refund_rows.append((refund_id, product["product_id"], refund_date.isoformat(), amount))
    conn.executemany("INSERT INTO refunds VALUES (?, ?, ?, ?)", refund_rows)

    conn.commit()
    conn.close()


def top_customers_by_region(region, db_path=DB_PATH, year="2025"):
    """Total spend per customer in a given region, for a given year."""
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        """
        SELECT customer_id, customer_name, SUM(quantity * product_price) AS total_spend
        FROM sales_flat
        WHERE UPPER(customer_region) = UPPER(?)
          AND substr(sale_date, 1, 4) = ?
        GROUP BY customer_id, customer_name
        ORDER BY total_spend DESC
        LIMIT 10
        """,
        (region, year),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def customer_lifetime_value(customer_ids, db_path=DB_PATH):
    """Total historical spend for each of the given customer ids."""
    conn = sqlite3.connect(db_path)
    values = {}
    for customer_id in customer_ids:
        cur = conn.execute(
            "SELECT SUM(quantity * product_price) FROM sales_flat WHERE customer_id = ?",
            (customer_id,),
        )
        values[customer_id] = cur.fetchone()[0] or 0.0
    conn.close()
    return values


def net_revenue_by_product(db_path=DB_PATH):
    """Gross revenue minus refunds, per product."""
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        """
        SELECT
            s.product_id,
            s.product_name,
            SUM(s.quantity * s.product_price) AS gross_revenue,
            SUM(r.amount) AS total_refunds
        FROM sales_flat s
        JOIN refunds r ON r.product_id = s.product_id
        GROUP BY s.product_id, s.product_name
        ORDER BY s.product_id
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    rebuild_warehouse()
    print(f"Warehouse rebuilt at {DB_PATH}")

    top = top_customers_by_region("north")
    print("\nTop customers in North (2025):")
    for customer_id, name, spend in top[:5]:
        print(f"  {name}: {spend:,.2f}")

    sample_ids = [1, 2, 3, 4, 5]
    clv = customer_lifetime_value(sample_ids)
    print("\nLifetime value, sample customers:")
    for customer_id, value in clv.items():
        print(f"  Customer {customer_id}: {value:,.2f}")

    net = net_revenue_by_product()
    print("\nNet revenue by product (first 5):")
    for product_id, name, gross, refunded in net[:5]:
        print(f"  {name}: gross {gross:,.2f}, refunded {refunded:,.2f}")
