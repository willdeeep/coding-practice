"""A small S3-triggered order-ingestion pipeline.

Simulates the shape of a Lambda function triggered by new order files
landing in an S3 bucket: lists the objects under a prefix, downloads and
parses each as CSV, and loads the parsed rows into a local SQLite table.

AWS is mocked in-process with `moto` — no real account, network access, or
credentials are needed to run this.

Run it directly:

    python ingest.py
"""

import csv
import io
import os
import sqlite3

import boto3
from moto import mock_aws

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "orders.db")

BUCKET_NAME = "acme-orders-landing"
REGION = "eu-west-2"

# Not actually used to authenticate against real AWS — moto intercepts
# every boto3 call made in this process — but written the way a real
# Lambda handler's client setup often ends up looking in practice.
AWS_ACCESS_KEY_ID = "AKIAFAKEKEYFORTESTING1"
AWS_SECRET_ACCESS_KEY = "fake/secret+access/keyForTraining1234567890"

# The IAM policy the ingestion role actually runs under in production.
INGEST_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
    ],
}

ORDER_FILES = [
    "orders/2025-01-01/batch-1.csv",
    "orders/2025-01-01/batch-2.csv",
    "orders/2025-01-02/batch-1.csv",
]
ROWS_PER_FILE = 200


def _client():
    return boto3.client(
        "s3",
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def _seed_bucket():
    """Create the landing bucket and drop a few synthetic order files into it."""
    s3 = _client()
    s3.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": REGION},
    )

    order_id = 1
    for key in ORDER_FILES:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["order_id", "customer_id", "amount"])
        for _ in range(ROWS_PER_FILE):
            writer.writerow(
                [order_id, 1000 + order_id % 50, round(10 + (order_id % 97) * 1.5, 2)]
            )
            order_id += 1
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=buf.getvalue().encode("utf-8"))


def list_new_objects(bucket=BUCKET_NAME, prefix="orders/"):
    """List every object under the given prefix."""
    s3 = _client()
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj["Key"] for obj in response.get("Contents", [])]


def _ensure_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER,
            customer_id INTEGER,
            amount REAL,
            source_key TEXT
        )
        """
    )
    conn.commit()


def process_object(key, conn):
    """Download one S3 object, parse it as CSV, and load its rows."""
    s3 = _client()
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        body = response["Body"].read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(body))
        for row in reader:
            conn.execute(
                "INSERT INTO orders (order_id, customer_id, amount, source_key) VALUES (?, ?, ?, ?)",
                (row["order_id"], row["customer_id"], row["amount"], key),
            )
        conn.commit()
        print(f"Loaded {key}")
    except Exception as e:
        print(f"Failed to process {key}: {e}")


def run_ingest():
    """Process every object currently under the orders/ prefix."""
    conn = sqlite3.connect(DB_PATH)
    _ensure_table(conn)

    for key in list_new_objects():
        process_object(key, conn)

    conn.close()


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with mock_aws():
        _seed_bucket()

        run_ingest()
        print("--- simulating a redelivered S3 event / Lambda retry ---")
        run_ingest()

    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    print(f"\nTotal rows loaded: {count}")
