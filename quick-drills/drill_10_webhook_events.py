import sqlite3


def _ensure_table(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS events (event_id TEXT, event_type TEXT)")
    conn.commit()


def load_events(events: list[dict], conn: sqlite3.Connection):
    for event in events:
        conn.execute(
            "INSERT INTO events (event_id, event_type) VALUES (?, ?)",
            (event["event_id"], event["event_type"]),
        )
    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    _ensure_table(conn)

    batch = [{"event_id": "evt_1", "event_type": "order_created"}]
    load_events(batch, conn)
    print("--- webhook redelivers the same event ---")
    load_events(batch, conn)

    count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"Total events stored: {count}")
    conn.close()
