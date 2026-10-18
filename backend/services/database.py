import hashlib
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "app.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS fee_terms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  listing_id INTEGER NOT NULL,
  version INTEGER NOT NULL,
  commission_pct REAL NOT NULL CHECK (commission_pct >= 0 AND commission_pct <= 100),
  payer TEXT NOT NULL CHECK (payer IN ('buyer','seller','split')),
  due_when TEXT NOT NULL,
  covers TEXT NOT NULL,
  other_fees TEXT NOT NULL DEFAULT 'None',
  terms_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (listing_id, version)
);

CREATE TABLE IF NOT EXISTS inquiries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reference TEXT UNIQUE NOT NULL,
  listing_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  buyer_name TEXT NOT NULL,
  buyer_phone TEXT NOT NULL,
  buyer_email TEXT,
  message TEXT NOT NULL,
  listed_price_lkr REAL NOT NULL,
  fee_terms_id INTEGER NOT NULL,
  terms_hash TEXT NOT NULL,
  consent INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (fee_terms_id) REFERENCES fee_terms(id)
);

CREATE TABLE IF NOT EXISTS deals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  inquiry_id INTEGER NOT NULL,
  listing_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  use_agent INTEGER NOT NULL,
  agreed_price_lkr REAL NOT NULL,
  commission_pct REAL NOT NULL,
  platform_fee_lkr REAL NOT NULL,
  agent_fee_lkr REAL NOT NULL,
  buyer_confirmed INTEGER NOT NULL DEFAULT 0,
  seller_confirmed INTEGER NOT NULL DEFAULT 0,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (inquiry_id) REFERENCES inquiries(id)
);

CREATE TABLE IF NOT EXISTS deal_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  deal_id INTEGER NOT NULL,
  from_state TEXT,
  to_state TEXT NOT NULL,
  note TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (deal_id) REFERENCES deals(id)
);

CREATE TABLE IF NOT EXISTS ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  deal_id INTEGER NOT NULL,
  entry_type TEXT NOT NULL,
  amount_lkr REAL NOT NULL CHECK (amount_lkr >= 0),
  payer TEXT NOT NULL,
  payee TEXT NOT NULL,
  status TEXT NOT NULL,
  reference TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (deal_id) REFERENCES deals(id)
);
"""

# Insert-only tables: the database itself refuses edits and deletes.
LOCKED_TABLES = ["fee_terms", "inquiries", "deal_events", "ledger"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_con():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    for t in LOCKED_TABLES:
        con.executescript(f"""
        CREATE TRIGGER IF NOT EXISTS {t}_no_update BEFORE UPDATE ON {t}
        BEGIN SELECT RAISE(ABORT, '{t} records are locked and cannot be edited'); END;
        CREATE TRIGGER IF NOT EXISTS {t}_no_delete BEFORE DELETE ON {t}
        BEGIN SELECT RAISE(ABORT, '{t} records are locked and cannot be edited'); END;
        """)
    con.commit()
    con.close()


def _hash_terms(listing_id, version, commission_pct, payer, due_when, covers, other_fees) -> str:
    raw = "|".join(str(x) for x in
                   [listing_id, version, commission_pct, payer, due_when, covers, other_fees])
    return hashlib.sha256(raw.encode()).hexdigest()


def create_fee_terms(con, listing_id, commission_pct, payer, due_when, covers, other_fees="None"):
    """Always creates a NEW version. Old versions are never changed."""
    version = con.execute(
        "SELECT COALESCE(MAX(version), 0) + 1 FROM fee_terms WHERE listing_id=?",
        (listing_id,)).fetchone()[0]
    h = _hash_terms(listing_id, version, commission_pct, payer, due_when, covers, other_fees)
    cur = con.execute(
        "INSERT INTO fee_terms (listing_id, version, commission_pct, payer, due_when, covers, "
        "other_fees, terms_hash, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (listing_id, version, commission_pct, payer, due_when, covers, other_fees, h, now()))
    return cur.lastrowid, version


def latest_terms(con, listing_id):
    return con.execute(
        "SELECT * FROM fee_terms WHERE listing_id=? ORDER BY version DESC LIMIT 1",
        (listing_id,)).fetchone()
