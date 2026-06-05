"""R1–R4 sample bills and intents for offline testing."""

from __future__ import annotations

from api.schemas import (
    Assignment,
    BillExtraction,
    GroupPhrase,
    LineItem,
    SplitIntent,
)

R1_BILL = BillExtraction(
    restaurant="Brew & Bite Café",
    line_items=[
        LineItem(name="Cappuccino", qty=1, amount=180),
        LineItem(name="Grilled Chicken Sandwich", qty=1, amount=260),
        LineItem(name="Penne Arrabiata", qty=1, amount=320),
        LineItem(name="Fresh Lime Soda", qty=1, amount=120),
        LineItem(name="Brownie", qty=1, amount=160),
    ],
    subtotal=1040,
    service_charge=52,
    gst=55,
    discount=0,
    round_off=0,
    grand_total=1147,
)

R1_INTENT = SplitIntent(
    people=["Ravi", "Neha", "Sameer"],
    paid_by="Sameer",
    assignments=[
        Assignment(
            item_refs=["cappuccino", "sandwich", "grilled chicken"],
            consumers=["Ravi"],
            mode="individual",
        ),
        Assignment(item_refs=["penne", "arrabiata", "lime soda", "soda"], consumers=["Neha"], mode="individual"),
        Assignment(item_refs=["brownie"], consumers=["Sameer"], mode="individual"),
    ],
)

R2_BILL = BillExtraction(
    restaurant="Tamarind Kitchen",
    line_items=[
        LineItem(name="Paneer Butter Masala", qty=1, amount=320),
        LineItem(name="Dal Makhani", qty=1, amount=260),
        LineItem(name="Butter Naan", qty=4, amount=240),
        LineItem(name="Jeera Rice", qty=1, amount=180),
        LineItem(name="Gulab Jamun", qty=2, amount=120),
        LineItem(name="Masala Papad", qty=2, amount=100),
    ],
    subtotal=1220,
    service_charge=61,
    gst=64,
    discount=0,
    round_off=0,
    grand_total=1345,
)

R2_INTENT = SplitIntent(
    people=["Aman", "Priya", "Karan", "Sara"],
    paid_by="Priya",
    group_phrases=[GroupPhrase(phrase="four of us", resolved_to=["Aman", "Priya", "Karan", "Sara"])],
    assignments=[
        Assignment(item_refs=["gulab jamun"], consumers=["Priya", "Karan"], mode="shared"),
        Assignment(item_refs=["*remaining*"], consumers=["Aman", "Priya", "Karan", "Sara"], mode="shared"),
    ],
)

R3_BILL = BillExtraction(
    restaurant="The Daily Grind",
    line_items=[
        LineItem(name="Margherita Pizza", qty=1, amount=380),
        LineItem(name="Arrabiata Pasta", qty=1, amount=340),
        LineItem(name="Garlic Bread", qty=1, amount=160),
        LineItem(name="Craft Beer", qty=2, amount=500),
        LineItem(name="Virgin Mojito", qty=1, amount=180),
    ],
    subtotal=1560,
    service_charge=78,
    gst=82,
    discount=0,
    round_off=0,
    grand_total=1720,
)

R3_INTENT = SplitIntent(
    people=["Ishaan", "Meera", "Rohit"],
    paid_by="Rohit",
    assignments=[
        Assignment(
            item_refs=["pizza", "pasta", "garlic bread"],
            consumers=["Ishaan", "Meera", "Rohit"],
            mode="shared",
        ),
        Assignment(item_refs=["beer", "craft beer"], consumers=["Ishaan", "Rohit"], mode="shared"),
        Assignment(item_refs=["mojito"], consumers=["Meera"], mode="individual"),
    ],
)

R4_BILL = BillExtraction(
    restaurant="Spice Route",
    line_items=[
        LineItem(name="Chicken Biryani", qty=2, amount=560),
        LineItem(name="Veg Biryani", qty=1, amount=240),
        LineItem(name="Mutton Rogan Josh", qty=1, amount=420),
        LineItem(name="Raita", qty=2, amount=120),
        LineItem(name="Soft Drinks", qty=3, amount=180),
    ],
    subtotal=1520,
    service_charge=76,
    gst=68,
    discount=-228,
    round_off=0,
    grand_total=1436,
)

R4_INTENT = SplitIntent(
    people=["Dev", "Nikhil", "Anjali", "Farah"],
    paid_by="Anjali",
    assignments=[
        Assignment(
            item_refs=["chicken biryani"],
            consumers=["Dev", "Nikhil"],
            mode="individual",
        ),
        Assignment(item_refs=["veg biryani"], consumers=["Anjali"], mode="individual"),
        Assignment(item_refs=["mutton", "rogan josh"], consumers=["Farah"], mode="individual"),
        Assignment(
            item_refs=["raita", "soft drinks"],
            consumers=["Dev", "Nikhil", "Anjali", "Farah"],
            mode="shared",
        ),
    ],
    group_phrases=[
        GroupPhrase(phrase="common to all four", resolved_to=["Dev", "Nikhil", "Anjali", "Farah"])
    ],
)

FIXTURES: dict[str, tuple[BillExtraction, SplitIntent, str]] = {
    "R1": (R1_BILL, R1_INTENT, R1_BILL.restaurant or "R1"),
    "R2": (R2_BILL, R2_INTENT, R2_BILL.restaurant or "R2"),
    "R3": (R3_BILL, R3_INTENT, R3_BILL.restaurant or "R3"),
    "R4": (R4_BILL, R4_INTENT, R4_BILL.restaurant or "R4"),
}
