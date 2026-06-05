"""Bill arithmetic checks and reconciliation."""

from __future__ import annotations

from api.schemas import BillExtraction, MatchedSplit, PerPerson, Reconciliation


def validate_bill(bill: BillExtraction, flags: list[str]) -> None:
    line_sum = sum(item.amount for item in bill.line_items)
    if line_sum != bill.subtotal:
        flags.append(
            f"Extracted line items sum to ₹{line_sum} but printed subtotal "
            f"is ₹{bill.subtotal}"
        )

    computed = (
        bill.subtotal
        + bill.service_charge
        + bill.gst
        + bill.discount
        + round(bill.round_off)
    )
    if computed != bill.grand_total:
        flags.append(
            f"Printed components sum to ₹{computed} but grand total is "
            f"₹{bill.grand_total} — ₹{bill.grand_total - computed} unexplained"
        )


def validate_matched(matched: MatchedSplit, bill: BillExtraction, flags: list[str]) -> None:
    consumers_seen = {c for a in matched.allocations for c in a.consumers}
    for person in matched.people:
        if person not in consumers_seen:
            flags.append(f"Diner '{person}' has no assigned items")
    assigned_items = {a.line_item.name for a in matched.allocations}
    for item in bill.line_items:
        if item.name not in assigned_items:
            flags.append(f"Bill line '{item.name}' was never assigned to anyone")



def build_reconciliation(
    per_person: list[PerPerson],
    grand_total: int,
) -> Reconciliation:
    total = sum(p.total for p in per_person)
    return Reconciliation(
        sum_of_person_totals=total,
        matches_bill=(total == grand_total),
    )
