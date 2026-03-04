from datetime import datetime, timezone


def add_reminder(conn, user: str, text: str, due_at_iso: str) -> None:
    conn.execute(
        "INSERT INTO reminders (ts, user, text, due_at) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), user, text, due_at_iso),
    )
    conn.commit()


def fetch_due_reminders(conn):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user, text, due_at FROM reminders WHERE done = 0 AND due_at <= ?",
        (now,),
    )
    return cur.fetchall()


def mark_reminder_done(conn, reminder_id: int) -> None:
    conn.execute("UPDATE reminders SET done = 1 WHERE id = ?", (reminder_id,))
    conn.commit()
