"""Offline receipt matching for demo mode (no Anthropic API key)."""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

from api.services.fixtures import FIXTURES
from api.services.matcher import _tokens

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"
IMAGE_MATCH_THRESHOLD = 0.82


def is_offline_mode() -> bool:
    return not os.getenv("ANTHROPIC_API_KEY")


def _decode_image(b64: str):
    from PIL import Image

    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _image_fingerprint(b64: str) -> list[int]:
    img = _decode_image(b64).resize((48, 48)).convert("L")
    return list(img.get_flattened_data())


def _image_similarity(b64_a: str, b64_b: str) -> float:
    a = _image_fingerprint(b64_a)
    b = _image_fingerprint(b64_b)
    mse = sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)
    return 1.0 / (1.0 + mse / 500.0)


def _load_sample_base64(key: str) -> str | None:
    path = SAMPLES_DIR / f"{key}.png"
    if not path.is_file():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


def detect_fixture_from_image(receipt_base64: str) -> str | None:
    if not receipt_base64:
        return None
    best_key: str | None = None
    best_score = 0.0
    for key in FIXTURES:
        sample = _load_sample_base64(key)
        if not sample:
            continue
        score = _image_similarity(receipt_base64, sample)
        if score > best_score:
            best_score = score
            best_key = key
    if best_key and best_score >= IMAGE_MATCH_THRESHOLD:
        return best_key
    return None


def detect_fixture_from_description(description: str) -> str | None:
    text = description.lower()
    scores: dict[str, int] = {}
    for key, (bill, intent, _) in FIXTURES.items():
        score = 0
        for person in intent.people:
            if person.lower() in text:
                score += 12
        for item in bill.line_items:
            item_tokens = _tokens(item.name)
            if any(token in text for token in item_tokens if len(token) > 3):
                score += 4
        if bill.restaurant:
            for word in bill.restaurant.split():
                if len(word) > 3 and word.lower() in text:
                    score += 8
        scores[key] = score
    if not scores:
        return None
    best = max(scores, key=scores.get)
    if scores[best] >= 16:
        return best
    return None


def detect_fixture(receipt_base64: str, description: str) -> str | None:
    return detect_fixture_from_image(receipt_base64) or detect_fixture_from_description(description)
