"""Request/response schemas matching the assignment contract."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SplitRequest(BaseModel):
    receipt_base64: str
    description: str


class PerPerson(BaseModel):
    name: str
    items: list[str]
    subtotal: int
    tax_share: int
    service_share: int
    discount_share: int
    total: int


class Reconciliation(BaseModel):
    sum_of_person_totals: int
    matches_bill: bool


class SettleUpEntry(BaseModel):
    from_: str = Field(serialization_alias="from", validation_alias="from")
    to: str
    amount: int

    model_config = {"populate_by_name": True}


class SplitResponse(BaseModel):
    per_person: list[PerPerson]
    grand_total: int
    reconciliation: Reconciliation
    paid_by: str
    settle_up: list[SettleUpEntry]
    assumptions: list[str]
    flags: list[str]


class LineItem(BaseModel):
    name: str
    qty: float = 1.0
    amount: int


class BillExtraction(BaseModel):
    line_items: list[LineItem]
    subtotal: int
    service_charge: int = 0
    gst: int = 0
    discount: int = 0
    round_off: float = 0.0
    grand_total: int
    restaurant: str | None = None
    confidence_notes: list[str] = Field(default_factory=list)


class Assignment(BaseModel):
    item_refs: list[str]
    consumers: list[str]
    mode: str = "shared"


class GroupPhrase(BaseModel):
    phrase: str
    resolved_to: list[str]


class SplitIntent(BaseModel):
    people: list[str]
    paid_by: str | None = None
    assignments: list[Assignment] = Field(default_factory=list)
    group_phrases: list[GroupPhrase] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)


class ItemAllocation(BaseModel):
    line_item: LineItem
    consumers: list[str]
    share_label: str


class MatchedSplit(BaseModel):
    people: list[str]
    paid_by: str | None
    allocations: list[ItemAllocation]
    assumptions: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
