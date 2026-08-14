"""One-off script to generate realistic WhatsApp-forward-style screenshots
for demo/recording purposes. Not part of the app — just a prop generator.

Usage: python make_whatsapp_mockups.py
"""

import textwrap

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 720, 1000
CHAT_BG = (229, 221, 213)
HEADER_BG = (7, 94, 84)
BUBBLE_BG = (255, 255, 255)
FORWARD_GRAY = (140, 140, 140)
TEXT_COLOR = (30, 30, 30)
TIME_GRAY = (150, 150, 150)


def load_font(size, bold=False):
    names = ["arialbd.ttf", "arial.ttf"] if bold else ["arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def rounded_bubble(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def make_mockup(filename, contact_name, message_lines, timestamp="10:42 AM"):
    img = Image.new("RGB", (WIDTH, HEIGHT), CHAT_BG)
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([0, 0, WIDTH, 90], fill=HEADER_BG)
    header_font = load_font(30, bold=True)
    draw.text((70, 28), contact_name, fill=(255, 255, 255), font=header_font)
    # simple back-chevron + avatar circle for realism (plain shapes, no glyphs
    # that might be missing from the font and render as tofu boxes)
    draw.line([(35, 30), (20, 45), (35, 60)], fill=(255, 255, 255), width=4, joint="curve")
    draw.ellipse([WIDTH - 80, 20, WIDTH - 30, 70], fill=(200, 200, 200))

    # Bubble
    body_font = load_font(28)
    small_font = load_font(20)
    tiny_font = load_font(18)

    padding = 24
    bubble_left = 40
    bubble_right = WIDTH - 100
    bubble_width = bubble_right - bubble_left

    wrapped = []
    for line in message_lines:
        wrapped.extend(textwrap.wrap(line, width=34) or [""])

    line_height = 36
    text_block_height = line_height * len(wrapped)
    forwarded_height = 34
    bubble_top = 150
    bubble_height = forwarded_height + text_block_height + 70

    rounded_bubble(
        draw,
        [bubble_left, bubble_top, bubble_right, bubble_top + bubble_height],
        radius=14,
        fill=BUBBLE_BG,
    )

    # "Forwarded" label
    draw.text(
        (bubble_left + padding, bubble_top + 14),
        "Forwarded",
        fill=FORWARD_GRAY,
        font=small_font,
    )

    # Message text
    y = bubble_top + 14 + forwarded_height
    for line in wrapped:
        draw.text((bubble_left + padding, y), line, fill=TEXT_COLOR, font=body_font)
        y += line_height

    # Timestamp
    draw.text(
        (bubble_right - padding - 90, bubble_top + bubble_height - 32),
        timestamp,
        fill=TIME_GRAY,
        font=tiny_font,
    )

    img.save(filename)
    print(f"saved {filename}")


make_mockup(
    "whatsapp-forward-5g.png",
    "Family Group",
    [
        "Good morning everyone! Please forward to all your groups:",
        "5G towers are spreading coronavirus in cities, stay safe,",
        "share with everyone!!",
    ],
)

make_mockup(
    "whatsapp-forward-fee.png",
    "College Friends",
    [
        "URGENT: WhatsApp will start charging a monthly",
        "subscription fee from next month. Forward this message",
        "to 10 contacts to keep your account free!",
    ],
    timestamp="9:15 PM",
)
