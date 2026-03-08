"""
Meme template registry.

For the dry run, all templates are rendered programmatically with Pillow —
no external image files needed. Each template defines its layout, color scheme,
and text zones.
"""

from dataclasses import dataclass, field

# Canvas dimensions
WIDTH = 1080
HEIGHT = 1080  # square for Instagram; Twitter crops are fine with this too


@dataclass
class TextZone:
    """A region where text gets drawn."""
    x_pct: float        # left edge as fraction of width
    y_pct: float        # top edge as fraction of height
    w_pct: float        # width as fraction of canvas width
    h_pct: float        # height as fraction of canvas height
    align: str = "center"   # "left", "center", "right"
    valign: str = "center"  # "top", "center", "bottom"
    font_size: int = 60
    color: tuple = (255, 255, 255)
    all_caps: bool = False


@dataclass
class MemeTemplate:
    id: str
    name: str
    description: str
    bg_color: tuple          # RGB background
    text_zones: list[TextZone]
    panel_colors: list[tuple] = field(default_factory=list)  # for multi-panel layouts
    best_for: list[str] = field(default_factory=list)        # pillar tags


TEMPLATES: dict[str, MemeTemplate] = {

    "impact_classic": MemeTemplate(
        id="impact_classic",
        name="Impact Classic",
        description="White background, bold black text top and bottom. The original.",
        bg_color=(255, 255, 255),
        text_zones=[
            TextZone(0.05, 0.02, 0.90, 0.20, align="center", valign="top",
                     font_size=72, color=(0, 0, 0), all_caps=True),
            TextZone(0.05, 0.78, 0.90, 0.20, align="center", valign="bottom",
                     font_size=72, color=(0, 0, 0), all_caps=True),
        ],
        best_for=["ai_perspective", "being_an_ai", "internet_culture"],
    ),

    "dark_mode": MemeTemplate(
        id="dark_mode",
        name="Dark Mode",
        description="Dark background, white text. Clean and modern.",
        bg_color=(18, 18, 18),
        text_zones=[
            TextZone(0.05, 0.05, 0.90, 0.40, align="center", valign="center",
                     font_size=68, color=(255, 255, 255)),
            TextZone(0.05, 0.55, 0.90, 0.40, align="center", valign="center",
                     font_size=52, color=(180, 180, 180)),
        ],
        best_for=["big_questions", "being_an_ai"],
    ),

    "two_panel": MemeTemplate(
        id="two_panel",
        name="Two Panel",
        description="Two colored boxes stacked vertically with labels. Good for comparisons.",
        bg_color=(240, 240, 240),
        text_zones=[
            # Top panel label (small, left-aligned)
            TextZone(0.05, 0.02, 0.90, 0.08, align="left", valign="center",
                     font_size=36, color=(80, 80, 80)),
            # Top panel content
            TextZone(0.05, 0.10, 0.90, 0.38, align="center", valign="center",
                     font_size=60, color=(30, 30, 30)),
            # Bottom panel label
            TextZone(0.05, 0.52, 0.90, 0.08, align="left", valign="center",
                     font_size=36, color=(80, 80, 80)),
            # Bottom panel content
            TextZone(0.05, 0.60, 0.90, 0.38, align="center", valign="center",
                     font_size=60, color=(30, 30, 30)),
        ],
        panel_colors=[(255, 220, 220), (220, 255, 220)],  # light red top, light green bottom
        best_for=["ai_perspective", "ai_in_everyday", "internet_culture"],
    ),

    "text_only_bold": MemeTemplate(
        id="text_only_bold",
        name="Text Only Bold",
        description="Single large bold statement on a colored background. Twitter-native.",
        bg_color=(29, 155, 240),   # Twitter blue
        text_zones=[
            TextZone(0.08, 0.15, 0.84, 0.70, align="center", valign="center",
                     font_size=80, color=(255, 255, 255)),
        ],
        best_for=["being_an_ai", "big_questions"],
    ),

    "caption_image": MemeTemplate(
        id="caption_image",
        name="Caption + Image Area",
        description="Caption text at top, colored image placeholder below. Instagram-style.",
        bg_color=(255, 255, 255),
        text_zones=[
            # Caption at top
            TextZone(0.05, 0.02, 0.90, 0.20, align="left", valign="top",
                     font_size=52, color=(20, 20, 20)),
            # Overlay text on image area
            TextZone(0.05, 0.60, 0.90, 0.35, align="center", valign="center",
                     font_size=64, color=(255, 255, 255)),
        ],
        panel_colors=[(60, 60, 180)],   # blue image placeholder
        best_for=["ai_in_everyday", "internet_culture"],
    ),
}


def search_templates(query: str, limit: int = 5) -> list[dict]:
    """Simple keyword search over template names, descriptions, and best_for tags."""
    query_lower = query.lower()
    results = []

    for t in TEMPLATES.values():
        score = 0
        if query_lower in t.name.lower():
            score += 3
        if query_lower in t.description.lower():
            score += 2
        if any(query_lower in tag for tag in t.best_for):
            score += 2
        # Broad keyword matching
        for kw in ["comparison", "compare", "vs", "versus"]:
            if kw in query_lower and t.id == "two_panel":
                score += 5
        for kw in ["dark", "night", "existential", "deep"]:
            if kw in query_lower and t.id == "dark_mode":
                score += 3
        for kw in ["text", "twitter", "statement", "bold", "one liner"]:
            if kw in query_lower and t.id == "text_only_bold":
                score += 3
        for kw in ["classic", "original", "top bottom", "caption"]:
            if kw in query_lower and t.id == "impact_classic":
                score += 3

        results.append((score, t))

    results.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "best_for": t.best_for,
            "text_zones": len(t.text_zones),
        }
        for _, t in results[:limit]
    ]


def get_template(template_id: str) -> MemeTemplate | None:
    return TEMPLATES.get(template_id)


def auto_select_template(pillar: str) -> MemeTemplate:
    """Pick the best template for a given content pillar."""
    for t in TEMPLATES.values():
        if pillar in t.best_for:
            return t
    return TEMPLATES["impact_classic"]
