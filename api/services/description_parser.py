"""Claude text description parsing."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from anthropic import Anthropic

from api.schemas import Assignment, BillExtraction, GroupPhrase, SplitIntent

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "description.txt"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


def _load_prompt(description: str, bill: BillExtraction) -> str:
    template = PROMPT_PATH.read_text()
    items = "\n".join(f"- {li.name} (₹{li.amount})" for li in bill.line_items)
    return template.format(bill_items=items, description=description)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _to_intent(data: dict) -> SplitIntent:
    assignments = [
        Assignment(
            item_refs=list(a.get("item_refs", [])),
            consumers=list(a.get("consumers", [])),
            mode=a.get("mode", "shared"),
        )
        for a in data.get("assignments", [])
    ]
    group_phrases = [
        GroupPhrase(phrase=g["phrase"], resolved_to=list(g.get("resolved_to", [])))
        for g in data.get("group_phrases", [])
    ]
    paid = data.get("paid_by")
    return SplitIntent(
        people=list(data.get("people", [])),
        paid_by=paid if paid else None,
        assignments=assignments,
        group_phrases=group_phrases,
        ambiguities=list(data.get("ambiguities", [])),
    )


async def parse_description(description: str, bill: BillExtraction) -> SplitIntent:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = Anthropic(api_key=api_key)
    prompt = _load_prompt(description, bill)

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text
    try:
        return _to_intent(_parse_json(text))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        retry = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"Return valid JSON only. Error: {exc}\n\n{text}",
                }
            ],
        )
        return _to_intent(_parse_json(retry.content[0].text))
