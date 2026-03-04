from datetime import datetime, timezone


def save_memory(conn, user: str, text: str) -> None:
    conn.execute(
        "INSERT INTO memory (ts, user, text) VALUES (?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), user, text),
    )
    conn.commit()


def set_profile_note(conn, user: str, note: str) -> None:
    conn.execute(
        "INSERT INTO profiles (user, notes) VALUES (?, ?) "
        "ON CONFLICT(user) DO UPDATE SET notes = excluded.notes",
        (user, note),
    )
    conn.commit()


def get_profile_note(conn, user: str):
    cur = conn.cursor()
    cur.execute("SELECT notes FROM profiles WHERE user = ?", (user,))
    row = cur.fetchone()
    return row[0] if row else None
