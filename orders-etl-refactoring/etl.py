"""A small orders ETL pipeline.

Generates a synthetic batch of e-commerce orders, extracts them from CSV,
transforms them into per-category revenue records, rolls up a couple of
summary views, and loads the result into a local SQLite database.

Run it directly:

    python etl.py
"""

import csv
import os
import random
import sqlite3
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_CSV = os.path.join(DATA_DIR, "orders_raw.csv")
DB_PATH = os.path.join(DATA_DIR, "orders.db")

REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Clothing", "Home", "Toys", "Books"]
NUM_ORDERS = 2000


def generate_raw_orders(path=RAW_CSV, n=NUM_ORDERS):
    """Write `n` synthetic order rows to `path`, as if they'd come from an upstream system."""
    random.seed(42)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    start_date = datetime(2025, 1, 1)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["order_id", "customer_id", "region", "category", "quantity", "unit_price", "order_date"]
        )
        for i in range(n):
            order_date = start_date + timedelta(days=random.randint(0, 180))
            writer.writerow(
                [
                    i + 1,
                    random.randint(1000, 1999),
                    random.choice(REGIONS),
                    random.choice(CATEGORIES),
                    random.randint(1, 8),
                    round(random.uniform(4.99, 299.99), 2),
                    order_date.strftime("%Y-%m-%d"),
                ]
            )


def extract_orders(path=RAW_CSV):
    """Read the raw order rows back out of CSV."""
    f = open(path, "r")
    reader = csv.DictReader(f)
    rows = [row for row in reader]
    return rows


def transform_electronics(rows):
    result = []
    for row in rows:
        if row["category"] == "Electronics":
            try:
                revenue = float(row["quantity"]) * float(row["unit_price"])
                result.append({**row, "revenue": revenue})
            except Exception:
                pass
    return result


def transform_clothing(rows):
    result = []
    for row in rows:
        if row["category"] == "Clothing":
            try:
                revenue = float(row["quantity"]) * float(row["unit_price"])
                result.append({**row, "revenue": revenue})
            except Exception:
                pass
    return result


def transform_home(rows):
    result = []
    for row in rows:
        if row["category"] == "Home":
            try:
                revenue = float(row["quantity"]) * float(row["unit_price"])
                result.append({**row, "revenue": revenue})
            except Exception:
                pass
    return result


def transform_toys(rows):
    result = []
    for row in rows:
        if row["category"] == "Toys":
            try:
                revenue = float(row["quantity"]) * float(row["unit_price"])
                result.append({**row, "revenue": revenue})
            except Exception:
                pass
    return result


def transform_books(rows):
    result = []
    for row in rows:
        if row["category"] == "Books":
            try:
                revenue = float(row["quantity"]) * float(row["unit_price"])
                result.append({**row, "revenue": revenue})
            except Exception:
                pass
    return result


def category_totals(rows):
    """Attach each row's category revenue total, for a quick per-row view."""
    enriched = []
    for row in rows:
        total = 0.0
        for other in rows:
            if other["category"] == row["category"]:
                total += other["revenue"]
        enriched.append({**row, "category_total": total})
    return enriched


def region_summary(rows, cache={}):
    """Sum revenue per region, memoising the result for repeat calls."""
    if cache:
        return cache

    for row in rows:
        region = row["region"]
        cache[region] = cache.get(region, 0.0) + row["revenue"]

    return cache


def load_orders(rows, db_path=DB_PATH):
    """Load transformed rows into the `orders` table."""
    setup_conn = sqlite3.connect(db_path)
    setup_conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER,
            customer_id INTEGER,
            region TEXT,
            category TEXT,
            quantity INTEGER,
            unit_price REAL,
            order_date TEXT,
            revenue REAL,
            category_total REAL
        )
        """
    )
    setup_conn.commit()
    setup_conn.close()

    for row in rows:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO orders
                (order_id, customer_id, region, category, quantity, unit_price, order_date, revenue, category_total)
            VALUES
                ({row['order_id']}, {row['customer_id']}, '{row['region']}', '{row['category']}',
                 {row['quantity']}, {row['unit_price']}, '{row['order_date']}', {row['revenue']}, {row['category_total']})
            """
        )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    generate_raw_orders()
    raw_rows = extract_orders()
    print(f"Extracted {len(raw_rows)} raw orders")

    transformed = (
        transform_electronics(raw_rows)
        + transform_clothing(raw_rows)
        + transform_home(raw_rows)
        + transform_toys(raw_rows)
        + transform_books(raw_rows)
    )
    print(f"Transformed {len(transformed)} orders")
    assert len(transformed) == len(raw_rows), "Every raw order should map to exactly one transformed order"

    enriched = category_totals(transformed)
    summary = region_summary(enriched)
    print("Revenue by region:")
    for region, total in sorted(summary.items()):
        print(f"  {region}: {total:,.2f}")

    load_orders(enriched)
    print(f"Loaded {len(enriched)} orders into {DB_PATH}")
