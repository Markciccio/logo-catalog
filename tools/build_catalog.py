#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp"}


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
    args = parser.parse_args()

    logos_dir = Path(args.logos_dir)
    out_path = Path(args.output)
    base_url = args.base_url.rstrip("/")

    if not logos_dir.exists():
        raise SystemExit(f"Missing logos directory: {logos_dir}")

    files = sorted([p for p in logos_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXT])
    logos = []

    for file_path in files:
        key = normalize_key(file_path.stem)
        if not key:
            continue

        display_name = display_name_from_stem(file_path.stem)
        file_name_encoded = quote(file_path.name)
        url = f"{base_url}/{file_name_encoded}"
        logos.append(
            {
                "key": key,
                "displayName": display_name,
                "url": url,
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
