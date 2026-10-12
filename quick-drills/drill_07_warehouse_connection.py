WAREHOUSE_CONFIG = {
    "account": "xy98765.us-east-1",
    "user": "svc_reporting",
    "password": "Autumn2025!",
    "warehouse": "REPORTING_WH",
}


def describe_connection() -> str:
    return f"Connecting to {WAREHOUSE_CONFIG['account']} as {WAREHOUSE_CONFIG['user']}"


if __name__ == "__main__":
    print(describe_connection())
