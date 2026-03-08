"""
Content generation pipeline.

Flow:
  concept (from agent) → Claude structures it into text fields → Pillow renders image
  → returns content package (image path + platform captions)
"""

import json
import os
import uuid
from pathlib import Path

import anthropic

from src.content.templates import get_template, auto_select_template, MemeTemplate
from src.content.renderer import render_meme

OUTPUT_DIR = Path("output")


def _parse_concept_directly(concept: str, template: MemeTemplate, platforms: list[str]) -> dict:
    """
    Parse a structured concept string directly (no API call).
    Used in MOCK_AI=true mode. Concept is expected to have lines like:
      'Top text: ...' / 'Bottom text: ...' / 'Zone N text: ...' / 'Label: ...'
    Falls back to splitting the concept across zones.
    """
    import re
    lines = concept.strip().splitlines()
    zone_texts = []

    # Try to extract labeled lines
    labeled = {}
    for line in lines:
        m = re.match(r"^(?:Zone\s*\d+|Top|Bottom|Label|Content)\s*(?:panel\s*\w+)?\s*(?:text|label)?\s*[:\-]\s*(.+)", line, re.IGNORECASE)
        if m:
            zone_texts.append(m.group(1).strip().strip("'\""))

    # Pad or trim to match template zone count
    while len(zone_texts) < len(template.text_zones):
        zone_texts.append("")
    zone_texts = zone_texts[: len(template.text_zones)]

    # Build simple captions from the concept
    first_two_zones = [z for z in zone_texts if z][:2]
    short_summary = " / ".join(first_two_zones) if first_two_zones else concept[:100]

    captions = {}
    hashtags = {}
    for platform in platforms:
        captions[platform] = short_summary
        hashtags[platform] = ["AIhumor", "AImemes", "clawd"] if platform == "twitter" else \
                              ["AIhumor", "AImemes", "clawd", "memes", "artificialintelligence"]

    return {"text_zones": zone_texts, "captions": captions, "hashtags": hashtags}


def _structure_meme_text(concept: str, template: MemeTemplate, platforms: list[str]) -> dict:
    """
    Ask Claude to convert a free-form meme concept into structured text fields.
    Returns a dict with text_zones (list of strings) and per-platform captions.
    In MOCK_AI mode, parses the concept directly without an API call.
    """
    if os.environ.get("MOCK_AI", "false").lower() == "true":
        return _parse_concept_directly(concept, template, platforms)

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    zone_descriptions = "\n".join(
        f"  Zone {i+1}: {z.description if hasattr(z, 'description') else f'{z.align} text, font size {z.font_size}'}"
        for i, z in enumerate(template.text_zones)
    )

    platform_list = ", ".join(platforms)

    prompt = f"""You are writing text for a meme image using the "{template.name}" template.

Template description: {template.description}
Number of text zones: {len(template.text_zones)}

The meme concept is:
{concept}

Write the exact text for each zone. Be punchy and concise — meme text should be short.
Also write a caption and hashtags for each platform: {platform_list}

Respond ONLY with valid JSON in this exact format:
{{
  "text_zones": [
    "text for zone 1",
    "text for zone 2"
  ],
  "captions": {{
    "instagram": "caption text here",
    "twitter": "caption text here"
  }},
  "hashtags": {{
    "instagram": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"],
    "twitter": ["hashtag1", "hashtag2"]
  }}
}}

Rules:
- text_zones must have exactly {len(template.text_zones)} entries (use "" for zones you want blank)
- Keep each text zone under 80 characters
- Instagram caption: up to 150 chars, warm and slightly conversational
- Twitter caption: under 240 chars total including hashtags, punchy
- Hashtags: no # symbol, just the word
- The meme is made by an AI (me, Clawd). The tone is dry, curious, lightly self-aware.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def generate_meme(
    topic: str,
    pillar: str,
    concept: str,
    template_id: str | None = None,
    platforms: list[str] | None = None,
    use_ai_image_gen: bool = False,
) -> dict:
    """
    Full meme generation pipeline.
    Returns a content package dict with content_id, image_path, captions, etc.
    """
    if platforms is None:
        platforms = ["instagram", "twitter"]

    # Select template
    if template_id:
        template = get_template(template_id)
        if template is None:
            template = auto_select_template(pillar)
    else:
        template = auto_select_template(pillar)

    # Structure the meme text via Claude
    structured = _structure_meme_text(concept, template, platforms)

    text_zones = structured.get("text_zones", [""] * len(template.text_zones))
    captions = structured.get("captions", {})
    hashtags = structured.get("hashtags", {})

    # Render the image
    content_id = str(uuid.uuid4())[:8]
    image_path = OUTPUT_DIR / f"{content_id}.png"
    render_meme(template, text_zones, image_path)

    # Build per-platform post packages
    posts = {}
    for platform in platforms:
        caption = captions.get(platform, "")
        tags = hashtags.get(platform, [])
        hashtag_str = " ".join(f"#{t}" for t in tags)
        posts[platform] = {
            "caption": f"{caption}\n\n{hashtag_str}".strip(),
            "image_path": str(image_path),
        }

    # Save metadata
    meta_path = OUTPUT_DIR / f"{content_id}.json"
    meta = {
        "content_id": content_id,
        "topic": topic,
        "pillar": pillar,
        "concept": concept,
        "template_id": template.id,
        "template_name": template.name,
        "text_zones": text_zones,
        "image_path": str(image_path),
        "posts": posts,
        "status": "generated",
    }
    OUTPUT_DIR.mkdir(exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2))

    return {
        "content_id": content_id,
        "image_path": str(image_path),
        "template_used": template.name,
        "text_zones": text_zones,
        "posts": posts,
        "preview": (
            f"Image saved to {image_path}. "
            f"Text zones: {text_zones}. "
            f"Ready for your review."
        ),
    }


def reject_content(content_id: str, reason: str, retry_with_notes: str | None = None) -> dict:
    """Mark content as rejected in its metadata file."""
    meta_path = OUTPUT_DIR / f"{content_id}.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        meta["status"] = "rejected"
        meta["rejection_reason"] = reason
        if retry_with_notes:
            meta["retry_notes"] = retry_with_notes
        meta_path.write_text(json.dumps(meta, indent=2))
    return {"status": "rejected", "content_id": content_id}
