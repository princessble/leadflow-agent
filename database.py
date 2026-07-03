import sqlite3
from datetime import datetime

DB_FILE = "leads.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            service TEXT,
            status TEXT DEFAULT 'new',
            assigned_to TEXT,
            created_at TEXT,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_lead(name, contact, service):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        "INSERT INTO leads (name, contact, service, created_at, last_updated) VALUES (?, ?, ?, ?, ?)",
        (name, contact, service, now, now),
    )
    lead_id = c.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def get_open_leads():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, contact, service, status FROM leads WHERE status != 'closed' ORDER BY created_at")
    rows = c.fetchall()
    conn.close()
    return rows

def update_status(lead_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("UPDATE leads SET status = ?, last_updated = ? WHERE id = ?", (status, now, lead_id))
    updated = c.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def assign_lead(lead_id, user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("UPDATE leads SET assigned_to = ?, last_updated = ? WHERE id = ?", (user_id, now, lead_id))
    updated = c.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def get_stale_leads(minutes=30):
    """Leads still 'new' that haven't been updated in X minutes."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, contact, service, last_updated FROM leads WHERE status = 'new'")
    rows = c.fetchall()
    conn.close()

    stale = []
    for row in rows:
        lead_id, name, contact, service, last_updated = row
        then = datetime.fromisoformat(last_updated)
        age_minutes = (datetime.now() - then).total_seconds() / 60
        if age_minutes >= minutes:
            stale.append((lead_id, name, contact, service, int(age_minutes)))
    return stale