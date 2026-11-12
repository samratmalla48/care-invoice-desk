from review import transition


def settle(db, key, reference):
    if not reference.strip():
        raise ValueError("Enter the external payment reference.")
    transition(db, key, "Approved", "Paid", reference.strip())


def balances(db):
    return db.execute("SELECT state, COUNT(*) AS count, SUM(cents) AS total FROM invoice GROUP BY state ORDER BY state").fetchall()


def history(db):
    return db.execute("""SELECT i.supplier,i.ref,e.action,e.note,e.created
                         FROM event e JOIN invoice i ON i.id=e.invoice_id
                         ORDER BY e.id DESC""").fetchall()
