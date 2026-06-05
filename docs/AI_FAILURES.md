# Where the AI was wrong (3 examples)

## 1. GST total computed instead of transcribed

- **Wrong:** On an early R1 run, Claude returned `"gst": 54` but also wrote “5% of 1092 = 54.6” and sometimes `"grand_total": 1146` by summing its own math.
- **Caught:** `validate_bill` compared `subtotal + service + gst + discount + round_off` to `grand_total`; reconciliation failed.
- **Fix:** Receipt prompt v2 forbids calculating tax; use printed GST rounded to whole rupees (55 on R1) and keep `grand_total` from the bill only.

## 2. Hallucinated “Lime Juice” line item

- **Wrong:** Description said “lime soda”; model invented a separate **Lime Juice ₹130** not on R2/R1 bills.
- **Caught:** Line items sum ≠ subtotal flag; matcher could not map soda consistently.
- **Fix:** Description prompt v2 passes exact bill item names from OCR; matcher flags unknown refs.

## 3. “Each had chicken biryani” → shared ₹560 instead of ₹280 each

- **Wrong:** First parse used `mode: shared` for both Dev and Nikhil on the single ₹560 line → ₹280 each was correct but model initially put **full ₹560 on each** in an earlier JSON typo (consumers duplicated wrong).
- **Caught:** Person food subtotals exceeded subtotal; reconciliation `matches_bill: false`.
- **Fix:** Prompt v5 `mode: individual` for “each had X”; `_split_line_for_individuals` in matcher splits qty lines per diner.
