"""Golden tests for R1–R4 fixtures."""

from __future__ import annotations

import asyncio

import pytest

from api.services.calculator import compute_per_person, reconcile_grand_total
from api.services.fixtures import FIXTURES
from api.services.matcher import match_intent_to_bill
from api.services.pipeline import run_split
from api.services.settle_up import build_settle_up
from api.services.validator import build_reconciliation, validate_bill


@pytest.mark.parametrize("key,grand", [("R1", 1147), ("R2", 1345), ("R3", 1720), ("R4", 1436)])
def test_fixture_reconciles(key: str, grand: int) -> None:
    bill, intent, _ = FIXTURES[key]
    flags: list[str] = []
    validate_bill(bill, flags)
    matched = match_intent_to_bill(bill, intent)
    per_person, assumptions = compute_per_person(bill, matched)
    per_person = reconcile_grand_total(per_person, bill.grand_total, assumptions, flags)
    recon = build_reconciliation(per_person, bill.grand_total)
    assert recon.matches_bill, (key, recon, flags, [p.model_dump() for p in per_person])


@pytest.mark.asyncio
@pytest.mark.parametrize("key,grand", [("R1", 1147), ("R2", 1345), ("R3", 1720), ("R4", 1436)])
async def test_pipeline_fixture(key: str, grand: int) -> None:
    async def noop_receipt(_: str):
        raise AssertionError("should not call")

    async def noop_desc(_: str, __):
        raise AssertionError("should not call")

    resp = await run_split("", f"fixture:{key}", extract_receipt=noop_receipt, parse_description=noop_desc)
    assert resp.grand_total == grand
    assert resp.reconciliation.matches_bill


def test_r1_food_splits() -> None:
    bill, intent, _ = FIXTURES["R1"]
    matched = match_intent_to_bill(bill, intent)
    per_person, _ = compute_per_person(bill, matched)
    by_name = {p.name: p.subtotal for p in per_person}
    assert by_name["Ravi"] == 440
    assert by_name["Neha"] == 440
    assert by_name["Sameer"] == 160


def test_r1_settle_up() -> None:
    bill, intent, _ = FIXTURES["R1"]
    matched = match_intent_to_bill(bill, intent)
    per_person, assumptions = compute_per_person(bill, matched)
    flags: list[str] = []
    per_person = reconcile_grand_total(per_person, bill.grand_total, assumptions, flags)
    paid_by, settle = build_settle_up(per_person, matched.paid_by, flags)
    assert paid_by == "Sameer"
    assert len(settle) == 2
    assert all(s.to == "Sameer" for s in settle)
