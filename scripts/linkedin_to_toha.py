#!/usr/bin/env python3
"""Sync Toha data files from LinkedIn profile_parsed.json."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import OrderedDict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("linkedin_to_toha: install PyYAML (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from skills_catalog import (  # noqa: E402
    LINKEDIN_ALIASES,
    SKILL_BUTTONS_EN,
    SKILL_BUTTONS_PT,
    skill_meta_for_linkedin,
)

MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

def cert_exam_url(cert_name: str, authority: str) -> str:
    """Exam purchase, registration, or official program enrollment — not vendor homepages."""
    n = cert_name.lower()
    if "sdlc security" in n or "secureflag" in authority.lower():
        return "https://www.secureflag.com/security-training-for-developers/"
    if "capa" in n or "argo project associate" in n:
        return (
            "https://training.linuxfoundation.org/certification/"
            "certified-argo-project-associate-capa/"
        )
    if "lfc101" in n or "inclusive speaker" in n:
        return (
            "https://training.linuxfoundation.org/training/"
            "inclusive-speaker-orientation-lfc101/"
        )
    if "gitlab" in n:
        return (
            "https://training.linuxfoundation.org/certification/"
            "gitlab-certified-associate-gca/"
        )
    if "ckad" in n:
        return (
            "https://training.linuxfoundation.org/certification/"
            "certified-kubernetes-application-developer-ckad/"
        )
    if "cka" in n:
        return (
            "https://training.linuxfoundation.org/certification/"
            "certified-kubernetes-administrator-cka/"
        )
    if "pca" in n or "prometheus" in n:
        return (
            "https://training.linuxfoundation.org/certification/"
            "prometheus-certified-associate/"
        )
    if "itil" in n:
        return (
            "https://www.peoplecert.org/browse-certifications/"
            "it-governance-and-service-management/ITIL-1/itil-4-foundation-2565"
        )
    if "lpic" in n:
        return "https://www.lpi.org/register-for-exams"
    return ""


def merge_accomplishment_entry(
    cert: dict,
    existing: dict | None,
) -> dict:
    name = cert.get("name", "")
    authority = cert.get("authority", "")
    prev = existing or {}
    prev_org = prev.get("organization") or {}
    org_url = (prev_org.get("url") or "").strip() or cert_exam_url(name, authority)
    item: dict = {
        "name": name,
        "organization": {
            "name": authority,
            "url": org_url,
        },
    }
    if prev.get("image"):
        item["image"] = prev["image"]
    cert_url = (prev.get("certificateURL") or cert.get("url") or "").strip()
    if cert_url:
        item["certificateURL"] = cert_url
    for key in ("timeline", "courseOverview"):
        if prev.get(key):
            item[key] = prev[key]
    return item

COMPANY_URLS = {
    "Workday": "https://www.workday.com",
    "Amazon Web Services (AWS)": "https://aws.amazon.com",
    "HiPartners Capital&Work": "https://www.linkedin.com/company/hipartners/",
    "FX | Flow Intelligence": "https://www.linkedin.com/company/feixe/",
    "SHELFPIX": "https://www.linkedin.com/company/shelfpix/",
    "Magicorp Consultoria em Tecnologia da Informação Ltda": "",
    "Odin's Krieger Fest (Brazil)": "",
    "NerdWeek": "https://nerdweek.com.br/",
    "Aramax Vision Technologies Ltda": "",
    "GUINDASTEC - Guindastes e Serviços Técnicos LTDA": "https://www.guindastec.com.br/",
}

AUTHOR_SUMMARY_EN = [
    "Principal SRE on large-scale private cloud (OpenStack + Kubernetes)",
    "Air-gapped Kubernetes platform architecture and zero-downtime upgrades",
    "Former AWS support: Batch, EKS/ECS, and container HPC",
    "Computer vision and AI since 2013; agentic LLM ops automation today",
    "Co-founder of NerdWeek; advisor to Odin's Krieger Fest",
]

PT = {
    "author_greeting": "Olá, eu sou",
    "author_summary": [
        "SRE principal em nuvem privada em larga escala (OpenStack + Kubernetes)",
        "Arquitetura de plataforma Kubernetes air-gapped e upgrades sem downtime",
        "Ex-AWS: Batch, EKS/ECS e computação HPC em containers",
        "Visão computacional e IA desde 2013; automação operacional com LLMs hoje",
        "Co-fundador da NerdWeek; conselheiro do Odin's Krieger Fest",
    ],
    "site_description": (
        "SRE principal | Nuvem privada OpenStack e Kubernetes | "
        "Visão computacional e IA desde 2013, agentes LLM hoje."
    ),
    "about_designation": "Principal Site Reliability Engineer",
    "education_section_name": "Formação",
    "experiences_section_name": "Experiência",
    "skills_section_name": "Habilidades",
    "accomplishments_section_name": "Certificações",
    # EN section title set in write_accomplishments when not pt
    "about_section_name": "Sobre",
}

ABOUT_SUMMARY_PT = (
    "Principal Site Reliability Engineer na infraestrutura de nuvem privada em larga escala "
    "da Workday. Mais de 200 clusters OpenStack, 20.000 hypervisors e 100.000+ VMs, "
    "além de 70+ clusters Kubernetes por cima, gerenciados com Cluster API (CAPI/CAPO).\n\n"
    "Sou um dos dois arquitetos principais da nossa plataforma Kubernetes air-gapped e "
    "conduzimos upgrades in-place de 1.31 para 1.37 sem downtime usando Cilium. "
    "Também construo automação agêntica com IA/LLM que atua em alertas de produção: "
    "coleta logs, confirma o problema e executa playbooks Ansible determinísticos.\n\n"
    "Antes do OpenStack, passei seis anos projetando soluções cloud-native na AWS, "
    "da consultoria até a própria AWS. Os últimos três anos focaram em computação batch "
    "em containers: AWS Batch, ParallelCluster, EKS e ECS, com envolvimento profundo "
    "em cargas GPU, F1 e MPI. Criei o programa SME para AWS Batch. Trabalho com visão "
    "computacional e IA desde 2013 (OpenCV, Caffe), muito antes da onda atual.\n\n"
    "Certificado em CAPA (Argo) e GitLab, com experiência em Ansible, Terraform, ArgoCD, "
    "Prometheus e Helm.\n\n"
    "Fora do trabalho, co-administro a NerdWeek, um veículo de mídia com redatores no "
    "mundo todo, e oriento o Odin's Krieger Fest, festival de folk/viking metal na "
    "América do Sul.\n\n"
    "Aberto a conversas sobre papéis de liderança em plataforma e SRE. Fique à vontade "
    "para conectar."
)


def default_profile_path() -> Path:
    env = os.environ.get("LINKEDIN_PROFILE")
    if env:
        return Path(env).expanduser()
    return Path.home() / "tmp/linkedin/export/live-2026-11-11/profile_parsed.json"


def default_photo_path() -> Path:
    env = os.environ.get("LINKEDIN_PHOTO")
    if env:
        return Path(env).expanduser()
    return Path.home() / "tmp/linkedin/1714759018041.jpeg"


def clean_summary(text: str) -> str:
    if not text:
        return ""
    t = text.replace("\r\n", "\n").strip()
    t = re.sub(r"(Workday)(\d)", r"\1. \2", t)
    t = re.sub(r"(\.)([A-Z])", r".\n\n\2", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


def format_start(exp: dict) -> str:
    ex = exp.get("start_export") or {}
    month = ex.get("month")
    year = ex.get("year")
    if year and month:
        return f"{MONTHS[month - 1]} {year}"
    if year:
        return str(year)
    start = exp.get("start", "")
    if re.match(r"^\d{4}-\d{2}$", start):
        y, m = start.split("-")
        return f"{MONTHS[int(m) - 1]} {y}"
    return start


def format_end(exp: dict) -> str | None:
    if exp.get("end") == "present" or exp.get("end_export") is None:
        return None
    ex = exp.get("end_export") or {}
    month = ex.get("month")
    year = ex.get("year")
    if year and month:
        return f"{MONTHS[month - 1]} {year}"
    if year:
        return str(year)
    return exp.get("end")


def parse_responsibilities(description: str) -> list[str]:
    if not description:
        return []
    lines: list[str] = []
    for part in re.split(r"(?:^|\n)\s*•\s*", description):
        part = part.strip()
        if not part:
            continue
        for sub in re.split(r"\n+", part):
            sub = sub.strip()
            if sub and sub not in lines:
                lines.append(sub)
    if not lines:
        for sub in re.split(r"\n+", description.strip()):
            if sub.strip():
                lines.append(sub.strip())
    return lines


def group_experiences(experience: list[dict]) -> list[dict]:
    grouped: OrderedDict[str, dict] = OrderedDict()
    for exp in experience:
        name = exp.get("company", "")
        if name not in grouped:
            grouped[name] = {
                "company": {
                    "name": name,
                    "url": COMPANY_URLS.get(name, ""),
                    "location": exp.get("location", ""),
                },
                "positions": [],
            }
        elif exp.get("location") and not grouped[name]["company"].get("location"):
            grouped[name]["company"]["location"] = exp["location"]
        pos: dict = {
            "designation": exp.get("title", ""),
            "start": format_start(exp),
            "responsibilities": parse_responsibilities(exp.get("description", "")),
        }
        end = format_end(exp)
        if end:
            pos["end"] = end
        grouped[name]["positions"].append(pos)
    return list(grouped.values())


def yaml_dump(data: dict) -> str:
    return yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )


def write_author(path: Path, pt: bool) -> None:
    data = {
        "name": "Hugo Prudente",
        "nickname": "Hugo",
        "greeting": PT["author_greeting"] if pt else "Hi, I am",
        "image": "images/author/hugo.png",
        "contactInfo": {
            "email": "hugo.kenshin+site@gmail.com",
            "github": "hugoprudente",
            "linkedin": "hugoprudente",
        },
        "summary": PT["author_summary"] if pt else AUTHOR_SUMMARY_EN,
    }
    path.write_text(yaml_dump(data), encoding="utf-8")


def write_site(path: Path, profile: dict, pt: bool) -> None:
    if pt:
        desc = PT["site_description"]
    else:
        desc = profile.get("headline", "Platform engineering, SRE, and automation.").strip()
    data = {
        "copyright": "© Hugo Prudente",
        "description": desc,
        "openGraph": {
            "title": "Hugo Prudente",
            "type": "website",
            "description": desc,
            "image": "images/author/hugo.png",
            "url": "https://hugoprudente.github.io",
        },
    }
    path.write_text(yaml_dump(data), encoding="utf-8")


def _about_summary(path: Path, pt: bool, summary_en: str) -> str:
    if not pt:
        return summary_en
    if path.is_file():
        try:
            old = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            prev = (old.get("summary") or "").strip()
            if prev:
                return prev
        except yaml.YAMLError:
            pass
    return ABOUT_SUMMARY_PT


def write_about(path: Path, profile: dict, pt: bool) -> None:
    summary_en = clean_summary(profile.get("summary", ""))
    exp = profile.get("experience") or []
    designation = exp[0].get("title", "Principal Site Reliability Engineer") if exp else ""
    data = {
        "section": {
            "name": PT["about_section_name"] if pt else "About",
            "id": "about",
            "enable": True,
            "weight": 1,
            "showOnNavbar": True,
        },
        "designation": PT["about_designation"] if pt else designation,
        "company": {"name": "Workday", "url": "https://www.workday.com"},
        "summary": _about_summary(path, pt, summary_en),
        "socialLinks": [
            {
                "name": "Email",
                "icon": "fas fa-envelope",
                "url": "mailto:hugo.kenshin+site@gmail.com",
            },
            {"name": "Github", "icon": "fab fa-github", "url": "https://github.com/hugoprudente"},
            {
                "name": "LinkedIn",
                "icon": "fab fa-linkedin",
                "url": "https://www.linkedin.com/in/hugoprudente/",
            },
            {
                "name": "StackOverflow",
                "icon": "fab fa-stack-overflow",
                "url": "https://stackoverflow.com/users/1463918/hugo-prudente",
            },
        ],
    }
    path.write_text(yaml_dump(data), encoding="utf-8")


def skills_from_catalog(pt: bool) -> list[dict]:
    from skills_catalog import SKILLS, SKILL_SUMMARY_PT

    out: list[dict] = []
    for name, summary_en, categories, url, icon in SKILLS:
        summary = SKILL_SUMMARY_PT.get(name, summary_en) if pt else summary_en
        row: dict = {"name": name, "summary": summary, "categories": categories}
        if url:
            row["url"] = url
        if icon:
            row["icon"] = icon
        out.append(row)
    return out


def write_skills(path: Path, profile: dict, pt: bool) -> None:
    skills_block: list[dict] = []
    if path.is_file():
        try:
            old = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            skills_block = list(old.get("skills") or [])
        except yaml.YAMLError:
            pass
    if not skills_block:
        skills_block = skills_from_catalog(pt)

    for raw in profile.get("skills") or []:
        if skill_meta_for_linkedin(raw) is None:
            print(
                f"warning: LinkedIn skill {raw!r} not in skills catalog — run make regenerate-skills",
                file=sys.stderr,
            )

    data = {
        "section": {
            "name": PT["skills_section_name"] if pt else "Skills",
            "id": "skills",
            "enable": True,
            "weight": 2,
            "showOnNavbar": True,
            "filter": True,
        },
        "buttons": SKILL_BUTTONS_PT if pt else SKILL_BUTTONS_EN,
        "skills": skills_block,
    }
    path.write_text(yaml_dump(data), encoding="utf-8")


def write_experiences(path: Path, profile: dict, pt: bool) -> None:
    data = {
        "section": {
            "name": PT["experiences_section_name"] if pt else "Experience",
            "id": "experiences",
            "enable": True,
            "weight": 3,
            "showOnNavbar": True,
        },
        "experiences": group_experiences(profile.get("experience") or []),
    }
    path.write_text(yaml_dump(data), encoding="utf-8")


def write_education(path: Path, profile: dict, pt: bool) -> None:
    degrees = []
    for edu in profile.get("education") or []:
        start = (edu.get("start_export") or {}).get("year", "")
        end = (edu.get("end_export") or {}).get("year", "")
        timeframe = f"{start}-{end}" if start and end else str(start or end)
        degree_name = edu.get("degree", "")
        field = edu.get("field", "")
        name = f"{degree_name} ({field})" if field else degree_name
        entry: dict = {
            "name": name,
            "icon": "fa-graduation-cap",
            "timeframe": timeframe,
            "institution": {"name": edu.get("school", ""), "url": ""},
        }
        notes = (edu.get("notes") or "").strip()
        if notes:
            entry["customSections"] = [{"name": "Capstone", "content": notes}]
        degrees.append(entry)
    data = {
        "section": {
            "name": PT["education_section_name"] if pt else "Education",
            "id": "education",
            "enable": bool(degrees),
            "weight": 4,
            "showOnNavbar": bool(degrees),
        },
        "degrees": degrees,
    }
    path.write_text(yaml_dump(data), encoding="utf-8")


def write_accomplishments(path: Path, profile: dict, pt: bool) -> None:
    existing_by_name: dict[str, dict] = {}
    if path.is_file():
        try:
            old = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for row in old.get("accomplishments") or []:
                if row.get("name"):
                    existing_by_name[row["name"]] = row
        except yaml.YAMLError:
            pass

    acc = []
    for cert in profile.get("certifications") or []:
        name = cert.get("name", "")
        acc.append(merge_accomplishment_entry(cert, existing_by_name.get(name)))
    data = {
        "section": {
            "name": PT["accomplishments_section_name"] if pt else "Certifications",
            "id": "accomplishments",
            "enable": bool(acc),
            "weight": 5,
            "showOnNavbar": bool(acc),
        },
        "accomplishments": acc,
    }
    path.write_text(yaml_dump(data), encoding="utf-8")


def sync_photo(photo: Path, blog_root: Path, dry_run: bool) -> None:
    dest = blog_root / "assets/images/author/hugo.png"
    if dry_run:
        print(f"would copy photo {photo} -> {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if photo.suffix.lower() in {".jpg", ".jpeg"}:
        shutil.copy2(photo, dest.with_suffix(".jpg"))
        os.system(
            f'sips -s format png -z 512 512 "{photo}" --out "{dest}" >/dev/null 2>&1'
        )
    else:
        shutil.copy2(photo, dest)


def sync_lang(blog_root: Path, profile: dict, lang: str, dry_run: bool) -> None:
    pt = lang == "pt-br"
    base = blog_root / "data" / lang
    writers = [
        (base / "author.yaml", lambda p: write_author(p, pt)),
        (base / "site.yaml", lambda p: write_site(p, profile, pt)),
        (base / "sections/about.yaml", lambda p: write_about(p, profile, pt)),
        (base / "sections/skills.yaml", lambda p: write_skills(p, profile, pt)),
        (base / "sections/experiences.yaml", lambda p: write_experiences(p, profile, pt)),
        (base / "sections/education.yaml", lambda p: write_education(p, profile, pt)),
        (
            base / "sections/accomplishments.yaml",
            lambda p: write_accomplishments(p, profile, pt),
        ),
    ]
    for path, fn in writers:
        if dry_run:
            print(f"would write {path}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        fn(path)
        print(f"wrote {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=default_profile_path())
    parser.add_argument("--photo", type=Path, default=default_photo_path())
    parser.add_argument("--blog-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--lang", choices=("en", "pt-br", "both"), default="both")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-photo", action="store_true")
    args = parser.parse_args()

    if not args.profile.is_file():
        print(f"profile not found: {args.profile}", file=sys.stderr)
        return 1

    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    langs = ["en", "pt-br"] if args.lang == "both" else [args.lang]

    if not args.skip_photo and args.photo.is_file():
        sync_photo(args.photo, args.blog_root, args.dry_run)
    elif not args.skip_photo:
        print(f"warning: photo not found at {args.photo}", file=sys.stderr)

    for lang in langs:
        sync_lang(args.blog_root, profile, lang, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
