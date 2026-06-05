"""End-to-end split pipeline."""

from __future__ import annotations

import re

from api.schemas import BillExtraction, SplitIntent, SplitResponse
from api.services.calculator import compute_per_person, reconcile_grand_total
from api.services.fixtures import FIXTURES
from api.services.matcher import match_intent_to_bill
from api.services.offline import detect_fixture, is_offline_mode
from api.services.settle_up import build_settle_up
from api.services.validator import build_reconciliation, validate_bill, validate_matched


def _parse_fixture_description(description: str) -> tuple[BillExtraction, SplitIntent] | None:
    m = re.match(r"^\s*fixture:\s*(R[1-4])\s*$", description, re.I)
    if m:
        key = m.group(1).upper()
        bill, intent, _ = FIXTURES[key]
        return bill, intent
    return None


async def run_split(
    receipt_base64: str,
    description: str,
    *,
    extract_receipt,
    parse_description,
) -> SplitResponse:
    flags: list[str] = []
    assumptions: list[str] = []

    fixture = _parse_fixture_description(description)
    if fixture:
        bill, intent = fixture
        assumptions.append(f"Using built-in fixture {description.strip()}")
    elif is_offline_mode():
        if not receipt_base64 and not description.strip():
            flags.append("No receipt image or description provided")
            return _empty_response(flags, assumptions)
        key = detect_fixture(receipt_base64, description)
        if not key:
            flags.append(
                "Could not match to a sample receipt (R1–R4). "
                "Click an R1–R4 button, upload a sample from samples/, or use a matching description."
            )
            return _empty_response(flags, assumptions)
        bill, intent, label = FIXTURES[key]
        bill = bill.model_copy(deep=True)
        intent = intent.model_copy(deep=True)
        assumptions.append("Running in offline demo mode (no Anthropic API key)")
        from api.services.offline import detect_fixture_from_image

        if receipt_base64 and detect_fixture_from_image(receipt_base64):
            assumptions.append(f"Matched uploaded image to sample receipt {key} ({label})")
        else:
            assumptions.append(f"Inferred sample bill {key} ({label}) from description")
        assumptions.append(f"Using built-in split rules for sample {key}")
    else:
        if not receipt_base64:
            flags.append("No receipt image provided")
            return _empty_response(flags, assumptions)
        bill = await extract_receipt(receipt_base64)
        intent = await parse_description(description, bill)

    validate_bill(bill, flags)
    for note in bill.confidence_notes:
        flags.append(f"Receipt OCR: {note}")
    for amb in intent.ambiguities:
        flags.append(f"Ambiguous description: {amb}")
    matched = match_intent_to_bill(bill, intent)
    flags.extend(matched.flags)
    assumptions.extend(matched.assumptions)

    validate_matched(matched, bill, flags)

    per_person, calc_assumptions = compute_per_person(bill, matched)
    assumptions.extend(calc_assumptions)

    per_person = reconcile_grand_total(per_person, bill.grand_total, assumptions, flags)

    reconciliation = build_reconciliation(per_person, bill.grand_total)
    if not reconciliation.matches_bill:
        flags.append(
            f"Person totals sum to ₹{reconciliation.sum_of_person_totals} "
            f"but bill grand total is ₹{bill.grand_total}"
        )

    paid_by, settle_up = build_settle_up(per_person, matched.paid_by, flags)

    return SplitResponse(
        per_person=per_person,
        grand_total=bill.grand_total,
        reconciliation=reconciliation,
        paid_by=paid_by,
        settle_up=settle_up,
        assumptions=assumptions,
        flags=flags,
    )


def _empty_response(flags: list[str], assumptions: list[str]) -> SplitResponse:
    from api.schemas import Reconciliation

    return SplitResponse(
        per_person=[],
        grand_total=0,
        reconciliation=Reconciliation(sum_of_person_totals=0, matches_bill=False),
        paid_by="",
        settle_up=[],
        assumptions=assumptions,
        flags=flags,
    )
