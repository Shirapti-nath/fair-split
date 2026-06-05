# Edge cases

| Input | Handling | Verified |
|-------|----------|----------|
| No service charge on bill | `service_charge = 0`; allocate ₹0 to everyone | y — fixture tweak + unit test pattern |
| Printed total ≠ line items + tax + discount + round-off | `flags` with unexplained ₹; still target printed `grand_total` for reconciliation | y — validator on R1-style bills |
| Description mentions item not on bill | Flag `"no matching bill line"`; item excluded from split | y — matcher unit behavior |
| “Four of us” / named group | `group_phrases` → `assumptions`; consumers list on `*remaining*` | y — R2 fixture test |
| “Rest of us” without names | `ambiguities` + flag; no default diners | y — parser prompt + pipeline flags |
| Shared item, subset only (Gulab Jamun) | Equal split among Priya + Karan only | y — R2 fixture |
| Common pool (4 naan, 4 people) | ₹240/4 via integer `_split_amount` | y — R2 fixture |
| Uneven qty (2 beers, 2 people) | ₹500/2 → ₹250 each | y — R3 fixture |
| Bill-level % discount (WELCOME15) | Use printed **−228**, not recomputed 15% | y — R4 fixture; flag if OCR discount ≠ 15% of subtotal |
| Tip / packaging not in fairness rules | Not modeled; flag if OCR adds unknown line | n — manual policy only (no sample) |
| No payer in description | `paid_by: ""`, empty `settle_up`, flag | y — `settle_up.py` |
| Multiple debtors, one payer | One `{from, to, amount}` row per non-payer | y — R1/R2 settle-up tests |
| OCR wrong line price | Line sum ≠ subtotal flag; may fail `matches_bill` | y — validator |
| Duplicate item names on bill | Flag ambiguous match; may assign multiple lines | partial — matcher flags |
| “I” without a name | Parser `ambiguities`; flag in pipeline | y — prompt rule |
| `fixture:R1`…`R4` without image | Built-in bill + intent for CI/demo | y — `test_r1_r4.py` |
| Missing `ANTHROPIC_API_KEY` on live OCR | HTTP 503 with clear message | y — route handler |

### Stress cases to run manually

- Real photo receipts (blur, skew) — vision prompt v2–v3.
- Bill with no GST line — expect `gst: 0` from OCR or flag.
- Description item typo (“penne” vs “pasta”) — fuzzy matcher + flags.
