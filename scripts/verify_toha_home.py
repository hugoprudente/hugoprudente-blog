#!/usr/bin/env python3
"""Verify Toha home UI with host Playwright (pip). Run `make serve-toha` first."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from skills_catalog import SKILLS_SECTION_ENABLED  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--base-url",
        default="http://127.0.0.1:1313/en/",
        help="Toha home URL (default: local serve-toha EN)",
    )
    p.add_argument("--headed", action="store_true", help="Show Chromium window")
    p.add_argument("--headless", action="store_true", help="Run without UI")
    p.add_argument(
        "--pause",
        action="store_true",
        help="After checks, wait for Enter before closing (only with --headed)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    headless = args.headless or not args.headed

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "playwright not installed. Use: pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            resp = page.goto(args.base_url, wait_until="networkidle", timeout=60_000)
            if resp and resp.status >= 400:
                errors.append(f"HTTP {resp.status} for {args.base_url}")
        except Exception as e:
            print(f"Could not load {args.base_url}: {e}", file=sys.stderr)
            print("Is `make serve-toha` running on port 1313?", file=sys.stderr)
            browser.close()
            return 1

        nav = page.locator("#top-nav-items")
        nav_labels = ["Speaking", "Certifications", "Writing"]
        if SKILLS_SECTION_ENABLED:
            nav_labels.insert(1, "Skills")
        for label in nav_labels:
            link = nav.get_by_role("link", name=label)
            if link.count() == 0 or not link.first.is_visible():
                errors.append(f"navbar missing link: {label}")

        html = page.content()
        if "G-G73E6NWXR0" not in html:
            errors.append("GA4 id G-G73E6NWXR0 not in page")

        cert = page.locator(".accomplishments-section")
        cert.scroll_into_view_if_needed()
        if cert.locator("h1", has_text="Certifications").count() == 0:
            errors.append("Certifications section heading not found")
        tiles = cert.locator(".cert-tile")
        if tiles.count() < 5:
            errors.append(f"expected >= 5 cert tiles, got {tiles.count()}")
        badges = cert.locator(".cert-tile-badge-wrap img.accomplishment-badge")
        if badges.count() < 5:
            errors.append(f"expected >= 5 cert badges, got {badges.count()}")
        sdlc = cert.locator(".cert-tile", has_text="SDLC Security")
        if sdlc.count() == 0 or sdlc.locator("img.accomplishment-badge").count() == 0:
            errors.append("SecureFlag SDLC badge image missing on EN")
        if cert.locator('a[href="https://www.linuxfoundation.org"]').count() > 0:
            errors.append("generic linuxfoundation.org homepage link still present")
        lf_exam = cert.locator('a[href*="training.linuxfoundation.org"]')
        if lf_exam.count() < 4:
            errors.append(
                f"expected >= 4 LF exam/training links, got {lf_exam.count()}"
            )
        if cert.locator('a[href="https://www.axelos.com"]').count() > 0:
            errors.append("generic axelos.com homepage link still present")
        if cert.locator('a[href*="peoplecert.org"]').count() < 1:
            errors.append("ITIL PeopleCert exam link missing")
        view_cert = cert.get_by_role("link", name=re.compile(r"certificate", re.I))
        if view_cert.count() < 5:
            errors.append(f"expected >= 5 view-certificate links, got {view_cert.count()}")

        if SKILLS_SECTION_ENABLED:
            skills = page.locator(".skills-section")
            skills.scroll_into_view_if_needed()
            if skills.locator("h1", has_text="Skills").count() == 0:
                errors.append("Skills section heading not found")
            filter_buttons = skills.locator(".skill-filtr-control")
            if filter_buttons.count() != 9:
                errors.append(
                    f"expected 9 skill filter buttons (All + 8), got {filter_buttons.count()}"
                )
            cards = skills.locator(".filtr-item")
            if cards.count() < 40:
                errors.append(f"expected >= 40 skill cards, got {cards.count()}")
            skills.get_by_role("button", name="Cloud, Virtualization & Cloud Native").click()
            page.wait_for_timeout(300)
            if skills.locator('a.skill-card-link[href*="kubernetes.io"]').count() == 0:
                errors.append("Kubernetes skill link missing after platforms filter")
            if skills.locator('a.skill-card-link[href*="ebpf.io"]').count() == 0:
                errors.append("eBPF skill missing after platforms filter")
            if skills.locator('a.skill-card-link[href*="ceph.io"]').count() == 0:
                errors.append("Ceph skill missing after platforms filter")
            if skills.locator('a.skill-card-link[href*="argoproj.github.io"]').count() == 0:
                errors.append("Argo Project skill missing after platforms filter")
            skills.get_by_role("button", name="Security & Compliance").click()
            page.wait_for_timeout(300)
            if skills.locator('a.skill-card-link[href*="openbao.org"]').count() == 0:
                errors.append("OpenBAO skill missing after security filter")
            if skills.locator('a.skill-card-link[href*="checkov.io"]').count() == 0:
                errors.append("Secure SDLC skill missing after security filter")
            skills.get_by_role("button", name="Observability & SRE").click()
            page.wait_for_timeout(300)
            if skills.locator('a.skill-card-link[href*="slack.com"]').count() == 0:
                errors.append("Slack skill missing after observability filter")
            skills.get_by_role("button", name="Programming Languages").click()
            page.wait_for_timeout(300)
            if skills.locator('a.skill-card-link[href*="python.org"]').count() == 0:
                errors.append("Python skill missing after programming filter")
            if skills.locator('a.skill-card-link[href*="dev.java"]').count() == 0:
                errors.append("Java skill missing after programming filter")
            if skills.locator('a.skill-card-link[href*="opencv.org"]').count() == 0:
                errors.append("Computer Vision skill missing after programming filter")
            skills.get_by_role("button", name="Networking & Protocols").click()
            page.wait_for_timeout(300)
            if skills.locator('a.skill-card-link[href*="coredns.io"]').count() == 0:
                errors.append("CoreDNS skill missing after networking filter")
            skills.get_by_role("button", name="Essentials & Support").click()
            page.wait_for_timeout(300)
            if skills.locator('a.skill-card-link[href*="vim.org"]').count() == 0:
                errors.append("Vim skill missing after essentials filter")
            if skills.locator('a.skill-card-link[href=""]').count() > 0:
                errors.append("skill cards with empty href")
        else:
            if page.locator("#top-nav-items").get_by_role("link", name="Skills").count() > 0:
                errors.append("Skills navbar link present but SKILLS_SECTION_ENABLED is false")
            if page.locator(".skills-section").count() > 0:
                errors.append("Skills section rendered but SKILLS_SECTION_ENABLED is false")

        if args.pause and args.headed:
            input("Checks done — press Enter to close the browser… ")

        browser.close()

    if errors:
        print("UI verification FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"UI verification OK: {args.base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
