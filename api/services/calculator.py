"""Deterministic fair split — all rupee math lives here."""

from __future__ import annotations

from collections import defaultdict

from api.schemas import (
    BillExtraction,
    ItemAllocation,
    MatchedSplit,
    PerPerson,
)


def _split_amount(amount: int, n: int) -> list[int]:
    """Split amount into n integer shares; remainder rupees go to first shares."""
    if n <= 0:
        return []
    base, rem = divmod(amount, n)
    return [base + (1 if i < rem else 0) for i in range(n)]


def _allocate_proportional(
    people_subtotals: dict[str, int],
    pool: int,
) -> dict[str, int]:
    """Split integer pool across people proportional to food subtotals."""
    if pool == 0:
        return {name: 0 for name in people_subtotals}
    total_food = sum(people_subtotals.values())
    if total_food == 0:
        return {name: 0 for name in people_subtotals}

    names = list(people_subtotals.keys())
    raw = {n: pool * people_subtotals[n] / total_food for n in names}
    rounded = {n: round(raw[n]) for n in names}
    remainder = pool - sum(rounded.values())
    if remainder != 0:
        # Assign leftover rupees to largest food subtotal
        target = max(names, key=lambda n: people_subtotals[n])
        rounded[target] += remainder
    return rounded


def compute_per_person(
    bill: BillExtraction,
    matched: MatchedSplit,
) -> tuple[list[PerPerson], list[str]]:
    assumptions: list[str] = list(matched.assumptions)
    food: dict[str, int] = defaultdict(int)
    items_display: dict[str, list[str]] = defaultdict(list)

    for alloc in matched.allocations:
        n_consumers = len(alloc.consumers)
        if n_consumers == 0:
            continue
        shares = _split_amount(alloc.line_item.amount, n_consumers)
        for consumer, share in zip(alloc.consumers, shares):
            food[consumer] += share
            items_display[consumer].append(alloc.share_label)

    people = matched.people
    for name in people:
        food.setdefault(name, 0)
        items_display.setdefault(name, [])

    tax_shares = _allocate_proportional(dict(food), bill.gst)
    service_shares = _allocate_proportional(dict(food), bill.service_charge)
    discount_shares = _allocate_proportional(dict(food), bill.discount)

    per_person: list[PerPerson] = []
    for name in people:
        sub = food[name]
        tax = tax_shares[name]
        svc = service_shares[name]
        disc = discount_shares[name]
        total = sub + tax + svc + disc
        per_person.append(
            PerPerson(
                name=name,
                items=sorted(set(items_display[name])),
                subtotal=sub,
                tax_share=tax,
                service_share=svc,
                discount_share=disc,
                total=total,
            )
        )

    assumptions.append(
        "Tax, service charge, and discount allocated proportional to each "
        "person's food subtotal; rounding remainder assigned to largest subtotal."
    )
    return per_person, assumptions


def reconcile_grand_total(
    per_person: list[PerPerson],
    grand_total: int,
    assumptions: list[str],
    flags: list[str],
) -> list[PerPerson]:
    """Nudge totals so sum matches grand_total when within small tolerance."""
    current = sum(p.total for p in per_person)
    diff = grand_total - current
    if diff == 0:
        return per_person
    if abs(diff) > 2:
        flags.append(
            f"Sum of person totals ₹{current} differs from grand total "
            f"₹{grand_total} by ₹{diff} after rounding"
        )
        return per_person

    target = max(per_person, key=lambda p: p.subtotal)
    updated = []
    for p in per_person:
        if p.name == target.name:
            updated.append(
                PerPerson(
                    name=p.name,
                    items=p.items,
                    subtotal=p.subtotal,
                    tax_share=p.tax_share,
                    service_share=p.service_share,
                    discount_share=p.discount_share,
                    total=p.total + diff,
                )
            )
        else:
            updated.append(p)
    assumptions.append(
        f"₹{abs(diff)} bill reconciliation adjustment applied to {target.name}'s total"
    )
    return updated
