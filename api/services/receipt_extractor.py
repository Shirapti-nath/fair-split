"""Claude vision receipt extraction."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from anthropic import Anthropic

from api.schemas import BillExtraction, LineItem

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "receipt.txt"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


def _load_prompt() -> str:
    return PROMPT_PATH.read_text()


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _to_bill(data: dict) -> BillExtraction:
    items = [
        LineItem(
            name=i["name"],
            qty=float(i.get("qty", 1)),
            amount=int(i["amount"]),
        )
        for i in data.get("line_items", [])
    ]
    return BillExtraction(
        restaurant=data.get("restaurant"),
        line_items=items,
        subtotal=int(data["subtotal"]),
        service_charge=int(data.get("service_charge", 0)),
        gst=int(data.get("gst", 0)),
        discount=int(data.get("discount", 0)),
        round_off=float(data.get("round_off", 0)),
        grand_total=int(data["grand_total"]),
        confidence_notes=list(data.get("confidence_notes", [])),
    )


async def extract_receipt(receipt_base64: str) -> BillExtraction:
    from api.services.offline import has_valid_api_key

    if not has_valid_api_key():
        raise RuntimeError(
            "No valid Anthropic API key. Use sample receipts R1–R4 or click the R1–R4 demo buttons."
        )
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

    client = Anthropic(api_key=api_key)
    media_type = "image/jpeg"
    if receipt_base64.startswith("iVBORw0KGgo"):
        media_type = "image/png"

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=_load_prompt(),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": receipt_base64,
                        },
                    },
                    {"type": "text", "text": "Transcribe this receipt into JSON."},
                ],
            }
        ],
    )

    text = message.content[0].text
    try:
        data = _parse_json(text)
        return _to_bill(data)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        retry = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"Fix this to valid JSON only:\n{text}\n\nError: {exc}",
                }
            ],
        )
        data = _parse_json(retry.content[0].text)
        return _to_bill(data)
