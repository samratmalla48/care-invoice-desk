# Care Invoice Desk

A local invoice-to-payment workbench for a fictional community care provider. Submit a supplier invoice, review it, record an external payment and reconcile the balance at each stage. Python's standard library serves the interface and SQLite stores the register. See [business requirements and acceptance criteria](docs/business-case.md).

## Run

From this folder, run `py -3 app.py` on Windows or `python3 app.py` on macOS/Linux. Open http://127.0.0.1:8765. Stop with Ctrl+C. Records persist across restarts.

No environment variables, API keys or pip packages are required. Optional settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| PORT | 8765 | Local HTTP port |
| INVOICE_DB | invoices.sqlite3 beside app.py | SQLite database file. Its parent folder must exist and be writable. |

## Walk through the workflow

1. Submit a synthetic invoice from Example Mobility, reference DEMO-001, for AUD 125.50.
2. Try entering the same supplier and reference again. The register should keep one invoice.
3. Approve it with a note, then record payment reference DEMO-PAY-001. The paid balance should be AUD 125.50 and the audit history should show three events.
4. Submit a second invoice and reject it with a reason. Payment is available only on approved invoices.

## Design

The app writes each state transition and its audit entry in a single transaction. Currency is stored in cents. The local single-operator demo has no authentication or banking connection. Use fictional data.

Original portfolio implementation inspired by the [invoice-to-payment BA case study](https://github.com/MusayevJavid/invoice-to-payment-bpmn-ba-project).
