#!/usr/bin/env python3
"""Run fixture splits without pytest; writes TEST_OUTPUT.txt."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.calculator import compute_per_person, reconcile_grand_total
from api.services.fixtures import FIXTURES
from api.services.matcher import match_intent_to_bill
from api.services.validator import build_reconciliation

out = []
for key in ("R1", "R2", "R3", "R4"):
    bill, intent, _ = FIXTURES[key]
    matched = match_intent_to_bill(bill, intent)
    per_person, assumptions = compute_per_person(bill, matched)
    flags: list[str] = []
    per_person = reconcile_grand_total(per_person, bill.grand_total, assumptions, flags)
    recon = build_reconciliation(per_person, bill.grand_total)
    out.append(f"{key}: matches={recon.matches_bill} sum={recon.sum_of_person_totals} grand={bill.grand_total}")
    for p in per_person:
        out.append(f"  {p.name}: sub={p.subtotal} total={p.total} items={p.items}")

Path(ROOT / "TEST_OUTPUT.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
