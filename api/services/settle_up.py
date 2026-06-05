"""Who owes whom after split."""

from __future__ import annotations

from api.schemas import PerPerson, SettleUpEntry


def build_settle_up(
    per_person: list[PerPerson],
    paid_by: str | None,
    flags: list[str],
) -> tuple[str, list[SettleUpEntry]]:
    if not paid_by:
        flags.append("No payer named in description")
        return "", []

    paid_by_norm = paid_by.strip()
    names = {p.name for p in per_person}
    if paid_by_norm not in names:
        flags.append(f"Payer '{paid_by_norm}' is not among the diners")

    entries: list[SettleUpEntry] = []
    for person in per_person:
        if person.name == paid_by_norm:
            continue
        entries.append(
            SettleUpEntry(
                from_=person.name,
                to=paid_by_norm,
                amount=person.total,
            )
        )
    return paid_by_norm, entries
