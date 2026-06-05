# Prompt log

| Version | Change | Why |
|---------|--------|-----|
| v1 receipt | Ask for JSON line items + printed totals only | Model added computed GST in prose |
| v2 receipt | Forbid calculating tax/service; `confidence_notes` for unclear fields | Reduce hallucinated surcharges |
| v3 receipt | Integer rupees for GST (round printed 54.60 → 55 on R1) | Match Indian bill rounding in code |
| v1 description | Parse people, assignments, paid_by | Baseline structured intent |
| v2 description | Inject bill item list from OCR into prompt | Fewer phantom items (“pasta” → wrong dish) |
| v3 description | `*remaining*` token for “everything else” | Reliable matcher for common-pool items |
| v4 description | `ambiguities[]` for unresolved “I” / vague groups | Flag instead of guessing diners |
| v5 description | `mode: individual` for “each had a biryani” | Correct qty-2 line split across Dev/Nikhil |

## Did the model do arithmetic?

**No.** Claude only transcribes the receipt (vision) and parses the description into people + item assignments. All rupee math — item splits, proportional tax/service/discount, rounding, reconciliation, and settle-up — runs in **Python** (`calculator.py`, `settle_up.py`, `validator.py`).

**Why:** Printed bills include round-off and discounts that models often mis-sum. A wrong confident total is worse than a flagged mismatch. Code enforces `reconciliation.matches_bill` and populates `flags` when components do not add up.
