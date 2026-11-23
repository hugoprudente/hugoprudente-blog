#!/usr/bin/env python3
"""Write data/en and data/pt-br sections/skills.yaml from skills_catalog."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from skills_catalog import (  # noqa: E402
    SKILL_BUTTONS_EN,
    SKILL_BUTTONS_PT,
    SKILLS,
    SKILLS_SECTION_ENABLED,
    SKILLS_SECTION_SHOW_ON_NAVBAR,
    SKILLS_SECTION_WEIGHT,
    SKILL_SUMMARY_PT,
    assert_catalog_consistency,
)


def build(buttons, section_name: str, pt: bool) -> dict:
    skills = []
    for name, summary_en, categories, url, icon in SKILLS:
        summary = SKILL_SUMMARY_PT.get(name, summary_en) if pt else summary_en
        skills.append(
            {
                "name": name,
                "summary": summary,
                "categories": categories,
                "url": url,
                "icon": icon,
            }
        )
    return {
        "section": {
            "name": section_name,
            "id": "skills",
            # Disabled on home/nav by default; flip constants in skills_catalog.py to restore.
            "enable": SKILLS_SECTION_ENABLED,
            "weight": SKILLS_SECTION_WEIGHT,
            "showOnNavbar": SKILLS_SECTION_SHOW_ON_NAVBAR,
            "filter": True,
        },
        "buttons": buttons,
        "skills": skills,
    }


def main() -> int:
    assert_catalog_consistency()
    for path, buttons, title, pt in (
        (ROOT / "data/en/sections/skills.yaml", SKILL_BUTTONS_EN, "Skills", False),
        (ROOT / "data/pt-br/sections/skills.yaml", SKILL_BUTTONS_PT, "Habilidades", True),
    ):
        data = build(buttons, title, pt)
        path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000),
            encoding="utf-8",
        )
        print(f"wrote {path} ({len(data['skills'])} skills, {len(data['buttons'])} filters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
