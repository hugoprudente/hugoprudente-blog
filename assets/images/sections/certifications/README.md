# Certification badge images

Square **400×400 PNG** after `normalize_cert_badges.py`. Reference in `data/*/sections/accomplishments.yaml` as:

`image: images/sections/certifications/<slug>.png`

## Pipeline

```bash
python3 scripts/fetch_cert_badge_images.py   # Credly only; keeps existing if new art is a banner
python3 scripts/normalize_cert_badges.py     # trim near-white, square canvas
```

**Credly:** `og:image` is often a LinkedIn **banner**, not the badge. The fetch script tries CDN `image.png` / `badge.png` and skips downgrades when aspect ratio &gt; 1.3.

**SecureFlag / non-Credly:** drop `secureflag.png` manually (certificate export), then normalize.

**ITIL:** replace `itil.png` manually if needed.

Org links in YAML = exam/training URLs; `certificateURL` = view certificate button.
