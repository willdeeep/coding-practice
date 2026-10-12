EXPORT_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {"Effect": "Allow", "Action": "*", "Resource": "*"},
    ],
}


def summarize_policy(policy: dict) -> str:
    stmt = policy["Statement"][0]
    return f"Allows {stmt['Action']} on {stmt['Resource']}"


if __name__ == "__main__":
    print(summarize_policy(EXPORT_ROLE_POLICY))
