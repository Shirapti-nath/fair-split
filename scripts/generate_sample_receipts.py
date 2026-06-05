#!/usr/bin/env python3
"""Generate text-based sample receipt PNGs for R1–R4 (requires Pillow)."""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("pip install pillow")
    raise

SAMPLES = {
    "R1.png": """Brew & Bite Café, Koramangala
12 Mar 2026  Bill #0142
Cappuccino          1   180
Grilled Chicken Sandwich 1 260
Penne Arrabiata     1   320
Fresh Lime Soda     1   120
Brownie             1   160
Subtotal                 1040
Service 5%                 52
GST                        55
Round-off                  +0
GRAND TOTAL              1147""",
    "R2.png": """Tamarind Kitchen, HSR Layout
14 Mar 2026  Bill #2207
Paneer Butter Masala 1  320
Dal Makhani          1  260
Butter Naan          4  240
Jeera Rice           1  180
Gulab Jamun          2  120
Masala Papad         2  100
Subtotal                1220
Service 5%                61
GST                       64
GRAND TOTAL              1345""",
    "R3.png": """The Daily Grind, Powai
15 Mar 2026  Bill #1188
Margherita Pizza     1  380
Arrabiata Pasta      1  340
Garlic Bread         1  160
Craft Beer           2  500
Virgin Mojito        1  180
Subtotal                1560
Service 5%                78
GST                       82
GRAND TOTAL              1720""",
    "R4.png": """Spice Route, Jubilee Hills
16 Mar 2026  Bill #5521
Chicken Biryani      2  560
Veg Biryani          1  240
Mutton Rogan Josh    1  420
Raita                2  120
Soft Drinks          3  180
Subtotal                1520
Discount WELCOME15      -228
Service 5%                76
GST                       68
GRAND TOTAL              1436""",
}


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "samples"
    out.mkdir(exist_ok=True)
    font = ImageFont.load_default()
    for name, text in SAMPLES.items():
        lines = text.split("\n")
        h = 24 + len(lines) * 18
        img = Image.new("RGB", (480, h), "white")
        draw = ImageDraw.Draw(img)
        y = 8
        for line in lines:
            draw.text((8, y), line, fill="black", font=font)
            y += 18
        img.save(out / name)
        print("wrote", out / name)


if __name__ == "__main__":
    main()
