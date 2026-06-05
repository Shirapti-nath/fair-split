"""Map description assignments to bill line items."""

from __future__ import annotations

import re

from api.schemas import (
    Assignment,
    BillExtraction,
    ItemAllocation,
    LineItem,
    MatchedSplit,
    SplitIntent,
)

REMAINING = "*remaining*"


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _tokens(text: str) -> set[str]:
    stop = {"the", "a", "an", "and", "with", "pc", "x"}
    return {t for t in _normalize(text).split() if t and t not in stop}


def _score_ref(ref: str, item_name: str) -> float:
    ref_n = _normalize(ref)
    name_n = _normalize(item_name)
    if ref_n == name_n:
        return 100.0
    if ref_n in name_n or name_n in ref_n:
        return 80.0
    ref_t = _tokens(ref)
    name_t = _tokens(item_name)
    if not ref_t:
        return 0.0
    overlap = len(ref_t & name_t) / len(ref_t)
    return overlap * 60.0


def _match_ref_to_items(ref: str, items: list[LineItem]) -> list[LineItem]:
    if ref == REMAINING:
        return []
    scored = [(item, _score_ref(ref, item.name)) for item in items]
    scored = [(i, s) for i, s in scored if s >= 30]
    if not scored:
        return []
    best_score = max(s for _, s in scored)
    return [i for i, s in scored if s >= best_score - 5]


def _share_label(item: LineItem, consumers: list[str], mode: str) -> str:
    n = len(consumers)
    if mode == "individual" or n == 1:
        return item.name
    if n == 2:
        return f"{item.name} (1/2)"
    return f"{item.name} (1/{n})"


def _split_line_for_individuals(item: LineItem, consumers: list[str]) -> list[tuple[LineItem, list[str]]]:
    """Each consumer gets their own slice when mode is individual on a multi-qty line."""
    if len(consumers) <= 1:
        return [(item, consumers)]
    per = item.amount / len(consumers)
    parts: list[tuple[LineItem, list[str]]] = []
    for consumer in consumers:
        parts.append(
            (
                LineItem(name=item.name, qty=1, amount=round(per)),
                [consumer],
            )
        )
    return parts


def match_intent_to_bill(
    bill: BillExtraction,
    intent: SplitIntent,
) -> MatchedSplit:
    assumptions: list[str] = list(
        f"'{gp.phrase}' interpreted as {', '.join(gp.resolved_to)}"
        for gp in intent.group_phrases
    )
    flags: list[str] = []
    people = list(intent.people)
    assigned: dict[str, ItemAllocation] = {}

    explicit_items: set[str] = set()

    for assignment in intent.assignments:
        if REMAINING in assignment.item_refs:
            continue
        for ref in assignment.item_refs:
            matches = _match_ref_to_items(ref, bill.line_items)
            if not matches:
                flags.append(f"Description mentions '{ref}' but no matching bill line found")
                continue
            if len(matches) > 1:
                flags.append(f"Ambiguous match for '{ref}' — using all close matches")
            for item in matches:
                explicit_items.add(item.name)
                consumers = [c for c in assignment.consumers if c in people]
                if not consumers:
                    flags.append(f"No valid consumers for '{ref}'")
                    continue
                if assignment.mode == "individual" and len(consumers) > 1:
                    for sub_item, sub_consumers in _split_line_for_individuals(item, consumers):
                        label = sub_item.name
                        key = f"{item.name}::{sub_consumers[0]}"
                        assigned[key] = ItemAllocation(
                            line_item=sub_item,
                            consumers=sub_consumers,
                            share_label=label,
                        )
                else:
                    label = _share_label(item, consumers, assignment.mode)
                    assigned[item.name] = ItemAllocation(
                        line_item=item,
                        consumers=consumers,
                        share_label=label,
                    )

    # Remaining assignments
    for assignment in intent.assignments:
        if REMAINING not in assignment.item_refs:
            continue
        consumers = [c for c in assignment.consumers if c in people]
        for item in bill.line_items:
            if item.name in explicit_items:
                continue
            if item.name in assigned:
                continue
            label = _share_label(item, consumers, assignment.mode)
            assigned[item.name] = ItemAllocation(
                line_item=item,
                consumers=consumers,
                share_label=label,
            )
        assumptions.append(
            f"Remaining unassigned items split among {', '.join(consumers)}"
        )

    allocations = list(assigned.values())
    return MatchedSplit(
        people=people,
        paid_by=intent.paid_by,
        allocations=allocations,
        assumptions=assumptions,
        flags=flags,
    )
