import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_db():
    """Return a new MySQL connection."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def query(sql, params=None, fetch=False, lastrowid=False):
    """
    Utility helper:
      fetch=True       → returns list of dicts
      lastrowid=True   → returns last inserted id
      else             → executes and commits
    """
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    if fetch:
        result = cur.fetchall()
        conn.close()
        return result
    if lastrowid:
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid
    conn.commit()
    conn.close()
