from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
import logging

log = logging.getLogger(__name__)

def get_db_connection(retries: int = 10, delay: int = 2):
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB", "certsdb"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                host=os.getenv("POSTGRES_HOST", "postgres"),
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            last_exception = e
            log.warning(f"DB connection failed (attempt {attempt}): {e}")
            time.sleep(delay)
    raise last_exception

@contextmanager
def db_cursor():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()