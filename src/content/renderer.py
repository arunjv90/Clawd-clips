"""
Pillow-based meme renderer.

Takes a MemeTemplate + text content and produces a PNG image.
No external image files required — all layouts are generated programmatically.
"""

import os
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.content.templates import MemeTemplate, TextZone, WIDTH, HEIGHT

# Try to find a usable bold font on the system
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _find_font() -> str | None:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


_SYSTEM_FONT = _find_font()


def _load_font(size: int) -> ImageFont.ImageFont:
    if _SYSTEM_FONT:
        try:
            return ImageFont.truetype(_SYSTEM_FONT, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines or [text]


def _draw_text_zone(
    draw: ImageDraw.ImageDraw,
    zone: TextZone,
    text: str,
    canvas_w: int = WIDTH,
    canvas_h: int = HEIGHT,
) -> None:
    if not text or not text.strip():
        return

    if zone.all_caps:
        text = text.upper()

    # Convert pct coords to pixels
    x = int(zone.x_pct * canvas_w)
    y = int(zone.y_pct * canvas_h)
    w = int(zone.w_pct * canvas_w)
    h = int(zone.h_pct * canvas_h)

    font = _load_font(zone.font_size)
    lines = _wrap_text(text, font, w, draw)

    # Calculate total text block height
    line_height = zone.font_size + 8
    total_h = len(lines) * line_height

    # Vertical alignment
    if zone.valign == "top":
        text_y = y
    elif zone.valign == "bottom":
        text_y = y + h - total_h
    else:  # center
        text_y = y + (h - total_h) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]

        if zone.align == "left":
            text_x = x
        elif zone.align == "right":
            text_x = x + w - line_w
        else:  # center
            text_x = x + (w - line_w) // 2

        # Light drop shadow for readability
        draw.text((text_x + 2, text_y + 2), line, font=font, fill=(0, 0, 0, 80))
        draw.text((text_x, text_y), line, font=font, fill=zone.color)

        text_y += line_height


def render_meme(
    template: MemeTemplate,
    texts: list[str],        # one string per text_zone, in order
    output_path: str | Path,
) -> Path:
    """
    Render a meme image and save it as a PNG.

    texts: list of strings, one per template.text_zones entry (in order).
           Pass empty string "" to leave a zone blank.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (WIDTH, HEIGHT), template.bg_color + (255,))
    draw = ImageDraw.Draw(img)

    # Draw panel backgrounds for multi-panel templates
    if template.id == "two_panel" and template.panel_colors:
        mid = HEIGHT // 2
        top_color = template.panel_colors[0]
        bot_color = template.panel_colors[1] if len(template.panel_colors) > 1 else template.panel_colors[0]
        draw.rectangle([0, int(0.09 * HEIGHT), WIDTH, mid - 4], fill=top_color)
        draw.rectangle([0, mid + int(0.09 * HEIGHT), WIDTH, HEIGHT], fill=bot_color)
        # Divider line
        draw.rectangle([0, mid - 4, WIDTH, mid + 4], fill=(200, 200, 200))

    elif template.id == "caption_image" and template.panel_colors:
        # Blue image placeholder in lower 55% of canvas
        draw.rectangle([0, int(0.25 * HEIGHT), WIDTH, HEIGHT], fill=template.panel_colors[0])

    # Draw each text zone
    for i, zone in enumerate(template.text_zones):
        text = texts[i] if i < len(texts) else ""
        _draw_text_zone(draw, zone, text)

    # Watermark
    wm_font = _load_font(28)
    draw.text((WIDTH - 220, HEIGHT - 42), "@clawd-clips 🤖", font=wm_font, fill=(150, 150, 150))

    img = img.convert("RGB")
    img.save(output_path, "PNG", quality=95)

    return output_path
