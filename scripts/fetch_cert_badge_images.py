#!/usr/bin/env python3
"""Download square certification badges from Credly. Run normalize_cert_badges.py after."""

from __future__ import annotations

import io
import re
import sys
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[misc, assignment]

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/images/sections/certifications"
MAX_ASPECT = 1.3
USER_AGENT = "Mozilla/5.0 (compatible; hugoprudente-blog/1.0)"

CERT_URLS = {
    "capa-argo": "https://www.credly.com/badges/14937d06-1532-4ece-80d6-56f17837c0e7",
    "lfc101": "https://www.credly.com/badges/6e5c4f13-8b85-459a-962c-73565724c023",
    "gitlab-associate": "https://www.credly.com/badges/a121a977-29d1-400d-9da5-b16b9249e387",
    "ckad": "https://www.credly.com/badges/9c87fa62-8cf4-491f-8706-e8eee008978e",
    "pca": "https://www.credly.com/badges/ac6a6130-d8e9-46fc-806e-58dce4686097",
    "cka": "https://www.credly.com/badges/d62654f8-4b23-4cc8-a0c8-abdaae7d6471",
}

OPTIONAL_URLS = {
    "lpic-1": "https://www.lpi.org/wp-content/uploads/2023/04/LPIC-1_0.jpg",
}


def fetch_bytes(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status != 200:
                return None
            return resp.read()
    except Exception:
        return None


def image_aspect(data: bytes) -> tuple[float, int, int] | None:
    if Image is None:
        return None
    try:
        with Image.open(io.BytesIO(data)) as im:
            w, h = im.size
            if h == 0:
                return None
            return max(w, h) / min(w, h), w, h
    except Exception:
        return None


def credly_image_uuid(page_url: str) -> str | None:
    m = re.search(r"credly\.com/badges/([0-9a-f-]+)", page_url, re.I)
    return m.group(1) if m else None


def credly_cdn_candidates(page_url: str, og_url: str | None) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    def add(u: str | None) -> None:
        if not u or u in seen:
            return
        seen.add(u)
        ordered.append(u)

    badge_uuid = credly_image_uuid(page_url)
    if badge_uuid:
        base = f"https://images.credly.com/images/{badge_uuid}"
        for name in (
            "image.png",
            "badge.png",
            "original.png",
            "facebook_thumb_print.png",
            "facebook_thumb_email.png",
        ):
            add(f"{base}/{name}")

    if og_url:
        add(og_url)
        m = re.search(r"(https://images\.credly\.com/images/[0-9a-f-]+)/", og_url, re.I)
        if m:
            base = m.group(1)
            for name in ("image.png", "badge.png", "original.png"):
                add(f"{base}/{name}")
        add(re.sub(r"/small\.png", "/large.png", og_url))

    return ordered


def fetch_og_image(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    m = re.search(r'property="og:image"\s+content="([^"]+)"', html)
    if not m:
        m = re.search(r"content=\"([^\"]+)\"\s+property=\"og:image\"", html)
    return m.group(1) if m else None


def pick_best_square(urls: list[str]) -> tuple[bytes, str] | None:
    best: tuple[bytes, str, float] | None = None
    for url in urls:
        data = fetch_bytes(url)
        if not data or len(data) < 500:
            continue
        meta = image_aspect(data)
        if not meta:
            continue
        aspect, w, h = meta
        score = (w * h) / aspect
        if best is None or score > best[2]:
            best = (data, url, score)
    if not best:
        return None
    data, url, _ = best
    return data, url


def existing_is_better(dest: Path, new_aspect: float) -> bool:
    if not dest.is_file() or Image is None:
        return False
    try:
        with Image.open(dest) as im:
            w, h = im.size
            old_aspect = max(w, h) / min(w, h)
            if old_aspect <= MAX_ASPECT and new_aspect > MAX_ASPECT:
                return True
            if old_aspect <= MAX_ASPECT and w * h > 80_000 and new_aspect > MAX_ASPECT:
                return True
    except Exception:
        pass
    return False


def fetch_credly(slug: str, page: str) -> None:
    dest = OUT / f"{slug}.png"
    og = None
    try:
        og = fetch_og_image(page)
    except Exception as e:
        print(f"warn {slug}: no og:image ({e})", file=sys.stderr)

    picked = pick_best_square(credly_cdn_candidates(page, og))
    if not picked:
        print(f"failed {slug}: no downloadable badge art", file=sys.stderr)
        return

    data, url = picked
    meta = image_aspect(data)
    if not meta:
        return
    aspect, w, h = meta
    if aspect > MAX_ASPECT and existing_is_better(dest, aspect):
        print(f"skipped {slug}: banner {w}x{h}; keeping existing", file=sys.stderr)
        return

    dest.write_bytes(data)
    print(f"saved {dest} from {url} ({w}x{h}, aspect {aspect:.2f})")


def fetch_optional(slug: str, url: str) -> None:
    dest = OUT / f"{slug}.png"
    if dest.exists() and dest.stat().st_size > 10_000:
        meta = image_aspect(dest.read_bytes())
        if meta and meta[0] <= MAX_ASPECT:
            return
    data = fetch_bytes(url)
    if not data:
        print(f"optional {slug} skipped", file=sys.stderr)
        return
    dest.write_bytes(data)
    print(f"saved {dest} from {url}")


def main() -> int:
    if Image is None:
        print("fetch_cert_badge_images: pip install pillow", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    for slug, page in CERT_URLS.items():
        try:
            fetch_credly(slug, page)
        except Exception as e:
            print(f"failed {slug}: {e}", file=sys.stderr)

    for slug, url in OPTIONAL_URLS.items():
        try:
            fetch_optional(slug, url)
        except Exception as e:
            print(f"optional {slug}: {e}", file=sys.stderr)

    print("note: secureflag.png is manual (not Credly)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
