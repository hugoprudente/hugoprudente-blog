#!/usr/bin/env python3
"""Normalize certification badges: trim padding, square 400px canvas, contain."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("normalize_cert_badges: pip install pillow", file=sys.stderr)
    raise SystemExit(1) from None

ROOT = Path(__file__).resolve().parents[1]
CERT_DIR = ROOT / "assets/images/sections/certifications"
CANVAS = 400
PADDING = 20
WHITE_THRESH = 248
SKIP = frozenset({"README.md"})


def trim_content(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    mpx = mask.load()
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 16:
                continue
            if r >= WHITE_THRESH and g >= WHITE_THRESH and b >= WHITE_THRESH:
                continue
            mpx[x, y] = 255
    bbox = mask.getbbox()
    if not bbox:
        return im
    return im.crop(bbox)


def normalize(path: Path) -> None:
    with Image.open(path) as raw:
        im = trim_content(raw)
        inner = CANVAS - 2 * PADDING
        im.thumbnail((inner, inner), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 0))
        x = (CANVAS - im.width) // 2
        y = (CANVAS - im.height) // 2
        canvas.paste(im, (x, y), im if im.mode == "RGBA" else None)
        out = path.with_suffix(".png")
        canvas.save(out, format="PNG", optimize=True)
        if out != path and path.suffix.lower() != ".png":
            path.unlink(missing_ok=True)
        ar = im.width / im.height if im.height else 1.0
        print(f"normalized {out.name} ({im.width}x{im.height}, ar={ar:.2f})")


def main() -> int:
    if not CERT_DIR.is_dir():
        print(f"missing {CERT_DIR}", file=sys.stderr)
        return 1
    for path in sorted(CERT_DIR.iterdir()):
        if path.name in SKIP or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        try:
            normalize(path)
        except Exception as e:
            print(f"failed {path.name}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
