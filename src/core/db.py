import psycopg2

from src.core.config import settings


def init_db():
    """Create the connections table if doesn't exists."""
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            thread_id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_all_sessions():
    """Returns all conversations sorted by most recent."""
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()
    cur.execute("SELECT thread_id, title FROM chat_sessions ORDER BY created_at DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1]} for r in rows]

def save_session(thread_id: str, title: str):
    """Saves a new session. If alredy exists, ignores."""
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_sessions (thread_id, title)
        VALUES (%s, %s)
        ON CONFLICT (thread_id) DO NOTHING;
    """, (thread_id, title))
    conn.commit()
    cur.close()
    conn.close()