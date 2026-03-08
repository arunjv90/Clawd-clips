"""
Post queue — dry-run mode.

In dry-run mode, posts are saved to output/queue.json and printed to stdout.
No actual publishing happens. Set DRY_RUN=false when ready to go live.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path("output")
QUEUE_FILE = OUTPUT_DIR / "queue.json"


def _load_queue() -> list[dict]:
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def _save_queue(queue: list[dict]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def schedule_post(
    content_id: str,
    platforms: list[str],
    post_at: str | None = None,
    priority: str = "normal",
) -> dict:
    """Add content to the posting queue."""
    dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"

    # Load content metadata
    meta_path = OUTPUT_DIR / f"{content_id}.json"
    if not meta_path.exists():
        return {"status": "error", "message": f"Content {content_id} not found"}

    meta = json.loads(meta_path.read_text())

    entry = {
        "content_id": content_id,
        "platforms": platforms,
        "priority": priority,
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "post_at": post_at or "next_optimal_slot",
        "dry_run": dry_run,
        "topic": meta.get("topic", ""),
        "template": meta.get("template_name", ""),
        "text_zones": meta.get("text_zones", []),
        "image_path": meta.get("image_path", ""),
    }

    # Add platform-specific post details
    for platform in platforms:
        if platform in meta.get("posts", {}):
            entry[f"{platform}_caption"] = meta["posts"][platform]["caption"]

    queue = _load_queue()
    queue.append(entry)
    _save_queue(queue)

    # Update content metadata status
    meta["status"] = "queued"
    meta_path.write_text(json.dumps(meta, indent=2))

    # Print a clear summary in dry-run mode
    if dry_run:
        print("\n" + "=" * 60)
        print("📋 DRY RUN — Post queued (not actually posted)")
        print("=" * 60)
        print(f"  Content ID : {content_id}")
        print(f"  Topic      : {meta.get('topic', '')}")
        print(f"  Template   : {meta.get('template_name', '')}")
        print(f"  Image      : {meta.get('image_path', '')}")
        print(f"  Platforms  : {', '.join(platforms)}")
        print(f"  Priority   : {priority}")
        for platform in platforms:
            caption = entry.get(f"{platform}_caption", "")
            if caption:
                print(f"\n  [{platform.upper()} caption]")
                print(f"  {caption[:300]}")
        print(f"\n  Meme text  : {meta.get('text_zones', [])}")
        print("=" * 60 + "\n")

    return {
        "status": "queued",
        "content_id": content_id,
        "platforms": platforms,
        "dry_run": dry_run,
        "queue_length": len(queue),
        "image_path": meta.get("image_path", ""),
    }


def get_queue() -> list[dict]:
    return _load_queue()
