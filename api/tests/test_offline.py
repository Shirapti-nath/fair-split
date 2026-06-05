"""Offline mode tests (no Anthropic API key)."""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from api.services.offline import detect_fixture_from_description, detect_fixture_from_image
from api.services.pipeline import run_split

SAMPLES = Path(__file__).resolve().parents[2] / "samples"

R1_DESCRIPTION = (
    "Three of us — Ravi, Neha, Sameer. Ravi had the cappuccino and the sandwich. "
    "Neha had the pasta and the lime soda. Sameer had the brownie. Sameer paid."
)


def test_detect_fixture_from_description_r1() -> None:
    assert detect_fixture_from_description(R1_DESCRIPTION) == "R1"


def test_detect_fixture_from_image_r1() -> None:
    b64 = base64.b64encode((SAMPLES / "R1.png").read_bytes()).decode("ascii")
    assert detect_fixture_from_image(b64) == "R1"


@pytest.mark.asyncio
async def test_pipeline_offline_r1_with_upload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    b64 = base64.b64encode((SAMPLES / "R1.png").read_bytes()).decode("ascii")

    async def fail_api(*_args, **_kwargs):
        raise AssertionError("Anthropic should not be called in offline mode")

    resp = await run_split(
        b64,
        R1_DESCRIPTION,
        extract_receipt=fail_api,
        parse_description=fail_api,
    )
    assert resp.grand_total == 1147
    assert resp.reconciliation.matches_bill
    assert resp.paid_by == "Sameer"


@pytest.mark.asyncio
async def test_pipeline_offline_r1_description_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    async def fail_api(*_args, **_kwargs):
        raise AssertionError("Anthropic should not be called in offline mode")

    resp = await run_split(
        "",
        R1_DESCRIPTION,
        extract_receipt=fail_api,
        parse_description=fail_api,
    )
    assert resp.grand_total == 1147
    assert resp.reconciliation.matches_bill
