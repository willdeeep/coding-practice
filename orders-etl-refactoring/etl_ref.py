"""A small orders ETL pipeline.

Generates a synthetic batch of e-commerce orders, extracts them from CSV,
transforms them into per-category revenue records, rolls up a couple of
summary views, and loads the result into a local SQLite database.

Run it directly:

    python etl.py
"""

import csv
import os
import sqlite3
from datetime import date
from decimal import Decimal
from itertools import count
from typing import Any, Literal

from polyfactory.decorators import post_generated
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field, ValidationError

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_CSV = os.path.join(DATA_DIR, "orders_raw.csv")
DB_PATH = os.path.join(DATA_DIR, "orders.db")

NUM_ORDERS = 2000

ORDER_COUNTER = count(start=1001)


class Order(BaseModel):
    order_id: int  = Field(ge=1000, le=3000)
    customer_id: int  = Field(ge=1000, le=1999)
    region: Literal["North", "South", "East", "West"]
    category: Literal["Electronics", "Clothing", "Home", "Toys", "Books"]
    quantity: int  =  Field(ge=1, le=8)
    unit_price: Decimal = Field(ge=Decimal("4.99"), le=Decimal("299.99"))
    order_date: date = Field(ge=date(2025, 1, 1))


class OrderFactory(ModelFactory[Order]):
    __model__ = Order
    @post_generated
    @classmethod
    def order_id(cls) -> int:
        return next(ORDER_COUNTER)


def generate_raw_orders(path=RAW_CSV, n=NUM_ORDERS):
    """Write `n` synthetic order rows to `path`, as if they'd come from an upstream system."""
    test_orders = OrderFactory.batch(size=n)

    with open(path, mode="w", newline="") as f:
        # Pull headers straight from the model's structure
        writer = csv.DictWriter(f, fieldnames=Order.model_fields.keys())
        writer.writeheader()
        
        # Dump the instantiated model dict values
        for order in test_orders:
            writer.writerow(order.model_dump())


def _validate_row(raw_row: dict[str, Any]) -> tuple[Order | None, ValidationError | None]:
    """
    Guard function: Separated from CSV file handling.
    Takes a dict and evaluates it against the Pydantic schema.
    """
    try:
        return Order.model_validate(raw_row), None
    except ValidationError as e:
        return None, e


def extract_orders(path: str = RAW_CSV) -> tuple[list[Order], list[dict[str, Any]]]:
    """Read the raw order rows back out of CSV and validate them."""
    valid_orders: list[Order] = []
    failed_rows: list[dict[str, Any]] = []

    if not os.path.exists(path):
        print(f"Warning: File path not found at targets: {path}")
        return valid_orders, failed_rows

    with open(path, mode="r", encoding="utf-8") as f:
        for row_index, raw_row in enumerate(csv.DictReader(f), start=2):
            validated_order, error = _validate_row(raw_row)
            
            if validated_order:
                valid_orders.append(validated_order)
            else:
                failed_rows.append({
                    "row_index": row_index,
                    "data": raw_row,
                    "error": error.errors(include_url=False) if error else []
                })
                
    return valid_orders, failed_rows



def calculate_row_rev(rows: list[Order]) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        revenue = float(row.quantity) * float(row.unit_price)
        result.append({**row.model_dump(), "revenue": revenue})
        
    return result

# def transform_electronics(rows):
#     result = []
#     for row in rows:
#         if row["category"] in  "Electronics":
#             try:
#                 revenue = float(row["quantity"]) * float(row["unit_price"])
#                 result.append({**row, "revenue": revenue})
#             except Exception:
#                 pass
#     return result


# def transform_electronics(rows):
#     result = []
#     for row in rows:
#         if row["category"] == "Electronics":
#             try:
#                 revenue = float(row["quantity"]) * float(row["unit_price"])
#                 result.append({**row, "revenue": revenue})
#             except Exception:
#                 pass
#     return result


# def transform_clothing(rows):
#     result = []
#     for row in rows:
#         if row["category"] == "Clothing":
#             try:
#                 revenue = float(row["quantity"]) * float(row["unit_price"])
#                 result.append({**row, "revenue": revenue})
#             except Exception:
#                 pass
#     return result


# def transform_home(rows):
#     result = []
#     for row in rows:
#         if row["category"] == "Home":
#             try:
#                 revenue = float(row["quantity"]) * float(row["unit_price"])
#                 result.append({**row, "revenue": revenue})
#             except Exception:
#                 pass
#     return result


# def transform_toys(rows):
#     result = []
#     for row in rows:
#         if row["category"] == "Toys":
#             try:
#                 revenue = float(row["quantity"]) * float(row["unit_price"])
#                 result.append({**row, "revenue": revenue})
#             except Exception:
#                 pass
#     return result


# def transform_books(rows):
#     result = []
#     for row in rows:
#         if row["category"] == "Books":
#             try:
#                 revenue = float(row["quantity"]) * float(row["unit_price"])
#                 result.append({**row, "revenue": revenue})
#             except Exception:
#                 pass
#     return result


# def category_totals(rows):
#     """Attach each row's category revenue total, for a quick per-row view."""
#     enriched = []
#     for row in rows:
#         total = 0.0
#         for other in rows:
#             if other["category"] == row["category"]:
#                 total += other["revenue"]
#         enriched.append({**row, "category_total": total})
#     return enriched


# def region_summary(rows, cache=None):
#     """Sum revenue per region, memoising the result for repeat calls."""
#     if cache is None:
#         cache = {}
#     else:
#         return cache

#     for row in rows:
#         region = row["region"]
#         cache[region] = cache.get(region, 0.0) + row["revenue"]

#     return cache


def load_orders(rows, db_path=DB_PATH):
    """Load transformed rows into the `orders` table."""
    conn = sqlite3.connect(db_path)
    conn.execute(
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
    conn.commit()

    # sqlite3 can't bind Decimal directly — coerce here, at the DB boundary,
    # rather than changing what the Pydantic model itself represents.
    params = [{**row, "unit_price": float(row["unit_price"])} for row in rows]

    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO orders
            (order_id, customer_id, region, category, quantity, unit_price, order_date, revenue)
        VALUES
            (:order_id, :customer_id, :region, :category, :quantity, :unit_price, :order_date, :revenue)
        """,
        params,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    generate_raw_orders()
    raw_rows, failed_rows = extract_orders()
    print(f"Extracted {len(raw_rows)} raw orders")

    # transformed = (
    #     transform_electronics(raw_rows)
    #     + transform_clothing(raw_rows)
    #     + transform_home(raw_rows)
    #     + transform_toys(raw_rows)
    #     + transform_books(raw_rows)
    # )

    transformed_orders = calculate_row_rev(raw_rows)
    print(f"Transformed {len(transformed_orders)} orders")
    assert len(transformed_orders) == len(raw_rows), "Every raw order should map to exactly one transformed order"

    # enriched = category_totals(transformed_orders) not needed, column is a definitive copy of revenue, move groupby downstream
    # summary = region_summary(transformed_orders)
    # print("Revenue by region:")
    # for region, total in sorted(summary.items()):
    #     print(f"  {region}: {total:,.2f}")

    load_orders(transformed_orders)
    print(f"Loaded {len(transformed_orders)} orders into {DB_PATH}")
