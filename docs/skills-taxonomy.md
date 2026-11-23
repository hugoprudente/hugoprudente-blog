# Skills section taxonomy

Eight navbar filters, aligned with [CNCF landscape2](https://landscape.cncf.io/) groupings (Security & Compliance, Observability & Analysis, Networking, Orchestration, App Definition & Delivery, AI/ML) and the blog post categories. Landscape **OS** is a **card-only** category (`os`), dual-tagged with `platforms` — Linux (Debian, Gentoo, CentOS Stream, Kali) surfaces under Cloud, Virtualization & Cloud Native.

**Single source of truth:** [`scripts/skills_catalog.py`](../scripts/skills_catalog.py)

```bash
make regenerate-skills   # or: python3 scripts/regenerate_skills_yaml.py
```

LinkedIn sync refreshes filter **buttons** only; card rows come from regen. See [`docs/TOHA.md`](TOHA.md).

## Navbar filters (8 + All)

| Slug | EN button | PT button | Absorbed |
|------|-----------|-----------|----------|
| `platforms` | Cloud, Virtualization & Cloud Native | Nuvem, virtualização e cloud native | storage, `os` |
| `monitoring` | Observability & SRE | Observabilidade e SRE | messaging (ops notifications) |
| `security` | Security & Compliance | Segurança e compliance | new |
| `automation` | Automation & Delivery | Automação e entrega | messaging (event-driven) |
| `programming` | Programming Languages | Linguagens de programação | — |
| `ai-llm` | AI & LLM | IA e LLM | Computer Vision story |
| `protocols` | Networking & Protocols | Redes e protocolos | networking depth |
| `essentials` | Essentials & Support | Essenciais e suporte | support-software |

Card-only category: `os` (Linux, eBPF) — must pair with `platforms` (self-check enforces).

## LinkedIn endorsements → catalog card

| LinkedIn name | Card |
|---------------|------|
| Openstack | OpenStack |
| Kubernetes | Kubernetes |
| Cluster API | Cluster API |
| Linux | Linux |
| Prometheus | Prometheus |
| Site Reliability Engineering | Site Reliability Engineering |
| Large Language Models (LLM) | Large Language Models (LLM) |
| Computer Vision | Computer Vision |
| OpenCV | Computer Vision |
| Git | Git |
| Amazon Web Services (AWS) | Amazon Web Services (AWS) |
| Python | Python |
| Agentic AI Development | Agentic AI Development |
| Ansible | Ansible |
| OpenBAO | OpenBAO |
| Helm Charts | Helm Charts |
| Docker | Podman & Docker |
| Infrastructure as code (IaC) | Terraform |
| Argo | Argo Project |
| GitLab CI/CD | GitLab CI/CD |

## Security narrative (spine across cards)

SecureFlag → Kali (via Linux coursework note) → OpenBAO/secrets → **Secure SDLC & Supply-Chain Scanning** (gitleaks/Semgrep/Checkov/Snyk, Kyverno/PSS) → Cilium/eBPF policy → DNS & TLS.

## Cert context in summaries

- **CAPA** — Argo Project card: Workflows, CD, Rollouts, Events.
- **PCA** — Prometheus, Grafana, SRE, Slack/Alertmanager: PromQL, exporters, SLI/SLO, dashboarding.
- **CKA/CKAD**, **LPIC-1**, **ITIL**, **SecureFlag** — woven into Linux, Kubernetes, DNS & TLS, OpenBAO, OTRS, language cards.
