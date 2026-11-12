"""Invoice intake and SQLite storage. Monetary values are integer cents."""
import os
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("INVOICE_DB", Path(__file__).with_name("invoices.sqlite3")))

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db

def initialise(db):
    db.executescript("""
        CREATE TABLE IF NOT EXISTS invoice (
          id INTEGER PRIMARY KEY, supplier TEXT NOT NULL COLLATE NOCASE,
          ref TEXT NOT NULL COLLATE NOCASE, cents INTEGER NOT NULL CHECK(cents>0),
          state TEXT NOT NULL DEFAULT 'Submitted', UNIQUE(supplier,ref));
        CREATE TABLE IF NOT EXISTS event (
          id INTEGER PRIMARY KEY, invoice_id INTEGER NOT NULL REFERENCES invoice(id),
          action TEXT NOT NULL, note TEXT NOT NULL,
          created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    """)

def submit(db, supplier, ref, amount):
    supplier, ref, amount = supplier.strip(), ref.strip(), amount.strip()
    if not supplier or not ref or not re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,2})?", amount):
        raise ValueError("Enter a supplier, invoice number and positive AUD amount (up to two decimal places).")
    whole, _, fraction = amount.partition(".")
    cents = int(whole)*100 + int(fraction.ljust(2,"0"))
    if cents == 0:
        raise ValueError("The amount must be positive.")
    try:
        with db:
            key = db.execute("INSERT INTO invoice(supplier,ref,cents) VALUES(?,?,?)", (supplier,ref,cents)).lastrowid
            db.execute("INSERT INTO event(invoice_id,action,note) VALUES(?,?,?)", (key,"Submitted","Invoice received"))
    except sqlite3.IntegrityError as exc:
        raise ValueError("This supplier invoice has already been submitted.") from exc
    return key
