def transition(db, key, expected, target, note):
    with db:
        changed = db.execute("UPDATE invoice SET state=? WHERE id=? AND state=?", (target,key,expected))
        if changed.rowcount != 1:
            raise ValueError(f"Only a {expected.lower()} invoice can be moved to {target.lower()}.")
        db.execute("INSERT INTO event(invoice_id,action,note) VALUES(?,?,?)", (key,target,note))


def review(db, key, decision, reason):
    if decision not in ("Approved","Rejected"):
        raise ValueError("Select a valid decision.")
    if decision == "Rejected" and not reason.strip():
        raise ValueError("Give a reason for rejecting this invoice.")
    transition(db, key, "Submitted", decision, reason.strip())
