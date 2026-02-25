#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp"}
EXTENSION_PRIORITY = {
    ".png": 4,
    ".webp": 3,
    ".jpg": 2,
    ".jpeg": 1,
}


def normalize_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def display_name_from_stem(stem: str) -> str:
    parts = re.split(r"[_\-\s]+", stem.strip())
    parts = [p for p in parts if p]
    if not parts:
        return "Logo"
    return " ".join(p.capitalize() for p in parts)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_brand_map(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    if not path.exists():
        return {}, {}

    content = json.loads(path.read_text(encoding="utf-8"))
    aliases_raw = content.get("aliases", {})
    display_raw = content.get("displayNames", {})

    aliases = {}
    for k, v in aliases_raw.items():
        nk = normalize_key(k)
        nv = normalize_key(v)
        if nk and nv:
            aliases[nk] = nv

    display_names = {}
    for k, v in display_raw.items():
        nk = normalize_key(k)
        if nk and isinstance(v, str) and v.strip():
            display_names[nk] = v.strip()

    return aliases, display_names


def should_replace(existing: dict, candidate: dict) -> bool:
    existing_score = (
        EXTENSION_PRIORITY.get(existing["path"].suffix.lower(), 0),
        existing["path"].stat().st_size,
    )
    candidate_score = (
        EXTENSION_PRIORITY.get(candidate["path"].suffix.lower(), 0),
        candidate["path"].stat().st_size,
    )
    return candidate_score > existing_score


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SOFELYWALLET catalog.json from local logos")
    parser.add_argument(
        "--logos-dir",
        default="logos",
        help="Directory containing logo files (default: logos)",
    )
    parser.add_argument(
        "--output",
        default="catalog.json",
        help="Output catalog file path (default: catalog.json)",
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL where logo files are hosted (without trailing slash preferred)",
    )
    parser.add_argument(
        "--brand-map",
        default="brand-map.json",
        help="Optional JSON map with aliases/displayNames (default: brand-map.json)",
    )
    args = parser.parse_args()

    logos_dir = Path(args.logos_dir)
    out_path = Path(args.output)
    base_url = args.base_url.rstrip("/")
    brand_map_path = Path(args.brand_map)

    if not logos_dir.exists():
        raise SystemExit(f"Missing logos directory: {logos_dir}")

    aliases, display_names = load_brand_map(brand_map_path)
    files = sorted([p for p in logos_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXT])
    selected_by_key: dict[str, dict] = {}

    for file_path in files:
        raw_key = normalize_key(file_path.stem)
        if not raw_key:
            continue

        key = aliases.get(raw_key, raw_key)
        display_name = (
            display_names.get(key)
            or display_names.get(raw_key)
            or display_name_from_stem(file_path.stem)
        )

        candidate = {"path": file_path, "display_name": display_name}
        existing = selected_by_key.get(key)
        if existing is None or should_replace(existing, candidate):
            selected_by_key[key] = candidate

    logos = []
    for key in sorted(selected_by_key.keys()):
        file_path = selected_by_key[key]["path"]
        display_name = selected_by_key[key]["display_name"]
        logos.append(
            {
                "key": key,
                "displayName": display_name,
                "url": f"{base_url}/{quote(file_path.name)}",
                "sha256": sha256_file(file_path),
            }
        )

    manifest = {
        "version": dt.date.today().isoformat(),
        "logos": logos,
    }

    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} with {len(logos)} logos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
