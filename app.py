"""Local invoice workbench. Run with Python 3."""
from contextlib import closing
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from urllib.parse import parse_qs

from intake import connect, initialise, submit
from review import review
from settlement import balances, history, settle


def field(name, label, required=True):
    return f'<label>{label} <input name="{name}" maxlength="150" {"required" if required else ""}></label>'


def page(db):
    parts = ['''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Care Invoice Desk</title>
<style>body{font:16px/1.55 system-ui;color:#17332e;background:#f6f8f5;max-width:980px;margin:3% auto;padding:1rem}h1{font: bold 2.7rem Georgia}section,article{background:white;border:1px solid #ccd9d2;padding:1rem;margin:.7rem 0}form{display:flex;flex-wrap:wrap;gap:.6rem;align-items:end}label{display:grid}input,button{font:inherit;padding:.4rem}button{background:#176454;color:white;border:0;cursor:pointer}small{color:#425f56}</style>
<h1>Care Invoice Desk</h1><section><h2>Submit an invoice</h2><form action="/submit" method="post">''',
             field("supplier","Supplier"),field("ref","Invoice number"),field("amount","Amount (AUD)"),
             '<button>Submit invoice</button></form></section><h2>Invoice register</h2>']
    rows = db.execute("SELECT * FROM invoice ORDER BY id DESC").fetchall()
    if not rows:
        parts.append("<p>Your submitted invoices will appear here.</p>")
    for row in rows:
        key, state = row["id"], row["state"]
        parts.append(f'<article><b>{escape(row["supplier"])} · {escape(row["ref"])}</b> &nbsp; AUD {row["cents"]/100:,.2f} &nbsp; {state}')
        hidden = f'<input type="hidden" name="id" value="{key}">'
        if state == "Submitted":
            parts.extend(['<form method="post" action="/review">',hidden,field("reason","Decision note (required for rejection)",False),
                          '<button name="decision" value="Approved">Approve</button><button name="decision" value="Rejected">Reject</button></form>'])
        elif state == "Approved":
            parts.extend(['<form method="post" action="/settle">',hidden,field("reference","External payment reference"),'<button>Record payment</button></form>'])
        parts.append('</article>')
    parts.append('<h2>Balances by status</h2>')
    for row in balances(db):
        parts.append(f'<p>{row["state"]} · {row["count"]} invoice(s) · AUD {row["total"]/100:,.2f}</p>')
    parts.append('<h2>Audit history</h2><ol>')
    for row in history(db):
        parts.append('<li>' + ' · '.join(escape(row[k]) for k in ('created','supplier','ref','action','note')) + '</li>')
    return ''.join(parts) + '</ol></html>'


class Desk(BaseHTTPRequestHandler):
    def html(self, status, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != "/":
            return self.send_error(404)
        with closing(connect()) as db:
            self.html(200,page(db))

    def do_POST(self):
        port = self.server.server_port
        origins = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
        if self.headers.get("Origin") not in origins or "http://" + self.headers.get("Host","") not in origins:
            return self.send_error(403)
        try:
            length = int(self.headers.get("Content-Length",0))
            if not 0 < length <= 8192:
                return self.send_error(413)
            values = parse_qs(self.rfile.read(length).decode(),keep_blank_values=True)
            def get(name):
                return values.get(name,[""])[0]
            with closing(connect()) as db:
                if self.path == "/submit":
                    submit(db,get("supplier"),get("ref"),get("amount"))
                elif self.path == "/review":
                    review(db,int(get("id")),get("decision"),get("reason"))
                elif self.path == "/settle":
                    settle(db,int(get("id")),get("reference"))
                else:
                    return self.send_error(404)
        except ValueError as exc:
            return self.html(400, f'<p>{escape(str(exc))}</p><a href="/">Back to invoice desk</a>')
        self.send_response(303)
        self.send_header("Location","/")
        self.end_headers()


if __name__ == "__main__":
    with closing(connect()) as db:
        initialise(db)
    server = ThreadingHTTPServer(("127.0.0.1", int(os.getenv("PORT","8765"))), Desk)
    print(f"Care Invoice Desk: http://127.0.0.1:{server.server_port}",flush=True)
    server.serve_forever()

