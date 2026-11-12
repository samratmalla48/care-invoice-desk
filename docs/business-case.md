# Invoice controls for a care provider

A fictional community care provider receives supplier invoices for services such as transport and equipment hire. In an email-based process, finance staff cannot easily see whether an invoice is awaiting review or has already been paid. This portfolio prototype uses synthetic records and models three staff activities in a single local operator view.

| ID | Business requirement | Acceptance example |
|---|---|---|
| INV-01 | Finance records supplier, invoice reference and positive AUD amount. | The same supplier and reference with different casing cannot be entered twice. |
| INV-02 | Review a submitted invoice before settlement. | A rejection requires a reason. A rejected invoice cannot be paid. |
| INV-03 | Record a completed external payment against an approval. | Recording a payment requires a reference. A second settlement is refused. |
| INV-04 | Retain the sequence of decisions and reconcile amounts by state. | After settlement the amount moves from approved to paid and the history retains both events. |

Submitted → Approved → Paid. Submitted → Rejected ends the workflow. Rejected invoices remain on record. The operator records payments made elsewhere. Identity checks, bank integration and real participant data are outside the demo.
