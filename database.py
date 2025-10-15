import sqlite3
import pandas as pd
from config import DB_FILE

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS journals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        entry TEXT,
        reflection TEXT,
        summary TEXT,
        followups TEXT,
        tone TEXT,
        safety TEXT,
        sentiment REAL,
        emotion TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_entry(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO journals (timestamp, entry, reflection, summary, followups, tone, safety, sentiment, emotion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["timestamp"], data["entry"], data["reflection"], data["summary"],
        str(data["followups"]), data["tone"], data["safety"],
        data["sentiment"], data["emotion"]
    ))
    conn.commit()
    conn.close()

def load_entries():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM journals ORDER BY timestamp DESC", conn)
    conn.close()
    return df
