"""Canonical skills section: filter buttons and skill cards for Toha home.

Eight navbar filters (CNCF-landscape informed). Landscape/blog `os` is a
card-only category dual-tagged with `platforms` — no OS button.
"""

from __future__ import annotations

# Home section toggles (regenerate-skills writes these into skills.yaml)
SKILLS_SECTION_ENABLED = False
SKILLS_SECTION_SHOW_ON_NAVBAR = False
SKILLS_SECTION_WEIGHT = 11

SKILL_BUTTONS_EN = [
    {"name": "All", "filter": "all"},
    {"name": "Cloud, Virtualization & Cloud Native", "filter": "platforms"},
    {"name": "Observability & SRE", "filter": "monitoring"},
    {"name": "Security & Compliance", "filter": "security"},
    {"name": "Automation & Delivery", "filter": "automation"},
    {"name": "Programming Languages", "filter": "programming"},
    {"name": "AI & LLM", "filter": "ai-llm"},
    {"name": "Networking & Protocols", "filter": "protocols"},
    {"name": "Essentials & Support", "filter": "essentials"},
]

SKILL_BUTTONS_PT = [
    {"name": "Todas", "filter": "all"},
    {"name": "Nuvem, virtualização e cloud native", "filter": "platforms"},
    {"name": "Observabilidade e SRE", "filter": "monitoring"},
    {"name": "Segurança e compliance", "filter": "security"},
    {"name": "Automação e entrega", "filter": "automation"},
    {"name": "Linguagens de programação", "filter": "programming"},
    {"name": "IA e LLM", "filter": "ai-llm"},
    {"name": "Redes e protocolos", "filter": "protocols"},
    {"name": "Essenciais e suporte", "filter": "essentials"},
]

FILTER_SLUGS = frozenset(btn["filter"] for btn in SKILL_BUTTONS_EN if btn["filter"] != "all")
ALLOWED_CARD_CATEGORIES = FILTER_SLUGS | {"os"}

# Endorsements on profile_parsed.json (2026) → canonical card name
LINKEDIN_TO_CARD: dict[str, str] = {
    "Openstack": "OpenStack",
    "OpenStack": "OpenStack",
    "Kubernetes": "Kubernetes",
    "Cluster API": "Cluster API",
    "Linux": "Linux",
    "Prometheus": "Prometheus",
    "Site Reliability Engineering": "Site Reliability Engineering",
    "Large Language Models (LLM)": "Large Language Models (LLM)",
    "Computer Vision": "Computer Vision",
    "OpenCV": "Computer Vision",
    "Git": "Git",
    "Amazon Web Services (AWS)": "Amazon Web Services (AWS)",
    "Python": "Python",
    "Agentic AI Development": "Agentic AI Development",
    "Ansible": "Ansible",
    "OpenBAO": "OpenBAO",
    "Helm Charts": "Helm Charts",
    "Docker": "Podman & Docker",
    "Infrastructure as code (IaC)": "Terraform",
    "Argo": "Argo Project",
    "GitLab CI/CD": "GitLab CI/CD",
}

LINKEDIN_SKILLS_FROM_CV = list(LINKEDIN_TO_CARD.keys())

LINKEDIN_ALIASES = {
    **LINKEDIN_TO_CARD,
    "Java EE": "Java",
    "CloudFormation": "Terraform",
}

# name, summary_en, categories, url, icon
SKILLS: list[tuple[str, str, list[str], str, str]] = [
    (
        "OpenStack",
        "Private cloud at scale: 200+ clusters, 20,000 hypervisors, 100,000+ VMs, hypervisor "
        "lifecycle, and tenant operations.",
        ["platforms"],
        "https://www.openstack.org/",
        "fas fa-cloud",
    ),
    (
        "Amazon Web Services (AWS)",
        "Six years from consulting through Enterprise Deployment: Batch, ParallelCluster, EKS/ECS, "
        "GPU/F1/MPI HPC, CloudFormation/CDK/CodePipeline, Lambda/SNS/SQS/EventBridge, X-Ray POC, "
        "Terraform/GitLab/Airflow/Vault in customer stacks.",
        ["platforms"],
        "https://aws.amazon.com/",
        "fab fa-aws",
    ),
    (
        "Linux",
        "Distro breadth used professionally: Debian/Ubuntu servers, Gentoo fleets (Aramax/FX), "
        "CentOS Stream image pipelines at scale, and Kali for security coursework. LPIC-1-backed "
        "networking, storage, and troubleshooting fundamentals.",
        ["platforms", "os"],
        "https://www.kernel.org/",
        "fab fa-linux",
    ),
    (
        "Podman & Docker",
        "Container images and multi-stage builds with Podman (daemonless) and Docker; "
        "Skopeo for registry copy/sync; Kaniko for non-privileged image builds on Kubernetes.",
        ["platforms"],
        "https://podman.io/",
        "fab fa-docker",
    ),
    (
        "Kubernetes",
        "CKA: cluster administration, troubleshooting, upgrades, RBAC, and audit. CKAD: workloads, "
        "scheduling, and app observability. 70+ fleets on OpenStack; CAPI/CAPO; in-place upgrades "
        "1.31→1.37 on Cilium; kube-bench and platform hardening.",
        ["platforms"],
        "https://kubernetes.io/",
        "fas fa-dharmachakra",
    ),
    (
        "Cluster API",
        "Kubernetes fleet provisioning and lifecycle with CAPI/CAPO on OpenStack—air-gapped "
        "platform architecture.",
        ["platforms"],
        "https://cluster-api.sigs.k8s.io/",
        "fas fa-sitemap",
    ),
    (
        "Ceph",
        "Distributed storage operations and automated hardware-failure workflows across private-cloud data centers.",
        ["platforms"],
        "https://ceph.io/",
        "fas fa-database",
    ),
    (
        "Cilium",
        "CNI, kube-proxy replacement, Hubble observability, network policy, and zero-downtime "
        "in-place cluster upgrades.",
        ["platforms", "protocols", "security"],
        "https://cilium.io/",
        "fas fa-network-wired",
    ),
    (
        "eBPF",
        "Kernel observability and networking with BPF: Cilium datapath, flow visibility, "
        "and performance-safe policy on Linux.",
        ["platforms", "protocols", "os", "security"],
        "https://ebpf.io/",
        "fas fa-microchip",
    ),
    (
        "Helm Charts",
        "Packaging and delivery on Kubernetes; CAPA-aligned Helm/Kustomize patterns with Argo CD.",
        ["platforms", "automation"],
        "https://helm.sh/",
        "fas fa-ship",
    ),
    (
        "Argo Project",
        "CAPA breadth: Argo CD GitOps (platform rollouts and tuning), Workflows (DAGs, artifacts), "
        "Rollouts (canary/blue-green), and Events (triggers and sensors)—with Helm and Kustomize.",
        ["platforms", "automation"],
        "https://argoproj.github.io/",
        "fas fa-code-branch",
    ),
    (
        "OpenBAO",
        "Secrets evaluation on platform: rotation automation, Dex/OIDC integration context, "
        "and SecureFlag-aligned SDLC hardening.",
        ["security", "platforms"],
        "https://openbao.org/",
        "fas fa-key",
    ),
    (
        "Secure SDLC & Supply-Chain Scanning",
        "Chimera-scale AppSec: gitleaks, Semgrep, Checkov, and Snyk across 200+ repos—true-positive "
        "remediation vs suppression hygiene, Kyverno Pod Security + PolicyException hardening, "
        "stale-image triage, and SecureFlag-certified secure coding.",
        ["security", "automation"],
        "https://www.checkov.io/",
        "fas fa-user-shield",
    ),
    (
        "Prometheus",
        "PCA scope in production: scrape config, labels, PromQL, recording/alert rules, exporters, "
        "and Alertmanager handoff—OpenStack and Kubernetes platform metrics; agentic bot ingests "
        "firing alerts.",
        ["monitoring", "platforms"],
        "https://prometheus.io/",
        "fas fa-chart-line",
    ),
    (
        "Grafana",
        "Per-data-center hypervisor health and tenant self-service; PCA dashboarding with "
        "PromQL-backed panels and on-call views.",
        ["monitoring"],
        "https://grafana.com/",
        "fas fa-chart-area",
    ),
    (
        "Zabbix",
        "Monitoring and alerting on AWS migrations and product platforms (Aramax, ShelfPix, Jenkins).",
        ["monitoring"],
        "https://www.zabbix.com/",
        "fas fa-desktop",
    ),
    (
        "Amazon CloudWatch",
        "AWS metrics, logs, and alarms; X-Ray global POC from Enterprise Deployment support.",
        ["monitoring", "platforms"],
        "https://aws.amazon.com/cloudwatch/",
        "fab fa-aws",
    ),
    (
        "Site Reliability Engineering",
        "ITIL-aligned incident and service mindset; SLI/SLO practice with Prometheus/Grafana; "
        "toil reduction via Ansible/OpenStack automation; on-call for 200+ clusters.",
        ["monitoring", "platforms"],
        "https://sre.google/",
        "fas fa-heart-pulse",
    ),
    (
        "AWX",
        "Ansible automation controller with Dex SSO, job templates, and deterministic playbooks "
        "selected by the production LLM alert bot.",
        ["automation", "platforms"],
        "https://ansible.com/open-source",
        "fas fa-server",
    ),
    (
        "Vim",
        "Primary terminal editor for remote SRE work and quick config edits.",
        ["essentials"],
        "https://www.vim.org/",
        "fas fa-keyboard",
    ),
    (
        "Zed",
        "Structured editing for code and docs with low-latency collaboration.",
        ["essentials"],
        "https://zed.dev/",
        "fas fa-edit",
    ),
    (
        "VSCodium",
        "IDE builds and extensions without vendor telemetry; day-to-day development.",
        ["essentials"],
        "https://vscodium.com/",
        "fas fa-laptop-code",
    ),
    (
        "OTRS",
        "Ticket workflows for data-center operations, hardware failures, and ITIL-style service "
        "tracking on retail platforms.",
        ["essentials"],
        "https://otrs.com/",
        "fas fa-ticket-alt",
    ),
    (
        "MediaWiki",
        "Team runbooks and operational documentation (Aramax/FX migrations).",
        ["essentials"],
        "https://www.mediawiki.org/",
        "fab fa-wikipedia-w",
    ),
    (
        "Computer Vision",
        "Since 2013: OpenCV and Caffe on ShelfPix/Aramax—shelf analytics, Android NDK, Python/C++ "
        "pipelines; predates current LLM wave and complements Agentic ops work.",
        ["ai-llm", "programming"],
        "https://opencv.org/",
        "fas fa-eye",
    ),
    (
        "Python",
        "Automation, AWS Batch/Airflow integrations, LLM agents, Prometheus client instrumentation, "
        "and platform tooling.",
        ["programming", "automation"],
        "https://www.python.org/",
        "fab fa-python",
    ),
    (
        "Java",
        "Enterprise and web backends: Java EE (EJB, JPA, JSF/PrimeFaces), Maven microservices "
        "on Java 7/8, Hibernate, and Tomcat—from maintenance-automation platforms to BI with Pentaho.",
        ["programming"],
        "https://dev.java/",
        "fab fa-java",
    ),
    (
        "C++",
        "Qt UIs, Android NDK state machines, and on-device vision beside OpenCV/Caffe stacks.",
        ["programming"],
        "https://isocpp.org/",
        "fas fa-code",
    ),
    (
        "Go",
        "Studying for cloud-native tooling and Kubernetes ecosystem utilities (PCA client libs).",
        ["programming"],
        "https://go.dev/",
        "fas fa-code",
    ),
    (
        "Rust",
        "Studying for safe systems tooling and infrastructure-adjacent components.",
        ["programming"],
        "https://www.rust-lang.org/",
        "fas fa-cog",
    ),
    (
        "Git",
        "Version control for GitOps, Zuul gated commits, GitLab pipelines, and review workflows.",
        ["automation", "essentials"],
        "https://git-scm.com/",
        "fab fa-git-alt",
    ),
    (
        "Ansible",
        "Deterministic remediation playbooks, AWX production controller, and LLM-selected runbooks.",
        ["automation", "platforms"],
        "https://www.ansible.com/",
        "fas fa-cogs",
    ),
    (
        "Terraform",
        "IaC with Terraform, CloudFormation, CDK, and Troposphere—NerdWeek on AWS, customer "
        "Enterprise Deployment patterns.",
        ["automation", "platforms"],
        "https://www.terraform.io/",
        "fas fa-layer-group",
    ),
    (
        "Zuul CI",
        "Gated CI/CD for Kubernetes and private-cloud platforms (OpenInfra talks).",
        ["automation", "platforms"],
        "https://zuul-ci.org/",
        "fas fa-project-diagram",
    ),
    (
        "GitLab CI/CD",
        "GitLab Certified Associate: pipelines, SCM, and deployment automation.",
        ["automation", "platforms"],
        "https://about.gitlab.com/",
        "fab fa-gitlab",
    ),
    (
        "AWS Messaging",
        "SNS, SQS, and EventBridge—serverless and Argo Events–like integration patterns from "
        "AWS support.",
        ["platforms"],
        "https://aws.amazon.com/sns/",
        "fas fa-envelope",
    ),
    (
        "Slack",
        "Ops notifications and agentic alert bots tied to AWX, Alertmanager routing, and runbooks.",
        ["monitoring", "ai-llm"],
        "https://slack.com/",
        "fab fa-slack",
    ),
    (
        "CoreDNS",
        "In-cluster DNS for Kubernetes; platform alerts and runbooks.",
        ["protocols", "platforms"],
        "https://coredns.io/",
        "fas fa-sitemap",
    ),
    (
        "DNS & TLS",
        "LPIC-1 networking, Route 53, HTTP/TLS, and VPC reachability (consulting and posts).",
        ["protocols", "security"],
        "https://letsencrypt.org/",
        "fas fa-lock",
    ),
    (
        "Large Language Models (LLM)",
        "Production alert analysis, runbook selection, and Hugging Face–class model stacks.",
        ["ai-llm"],
        "https://huggingface.co/docs/transformers/",
        "fas fa-brain",
    ),
    (
        "Agentic AI Development",
        "Slack bot on AWX, Ansible executor, and Prometheus Alertmanager—collect logs, confirm "
        "issues, LLM picks deterministic playbooks.",
        ["ai-llm"],
        "https://github.com/langchain-ai/langchain",
        "fas fa-robot",
    ),
]

SKILL_SUMMARY_PT: dict[str, str] = {
    "OpenStack": "Nuvem privada em escala: 200+ clusters, 20k hypervisors, 100k+ VMs e ciclo de vida de tenants.",
    "Amazon Web Services (AWS)": "Seis anos da consultoria ao Enterprise Deployment: Batch, EKS/ECS, HPC, IaC e observabilidade.",
    "Linux": "Distribuições usadas profissionalmente: Debian/Ubuntu, Gentoo (Aramax/FX), CentOS Stream (pipelines de imagem) e Kali em formação de segurança. Fundamentos LPIC-1.",
    "Podman & Docker": "Imagens com Podman e Docker; Skopeo e Kaniko no Kubernetes.",
    "Kubernetes": "CKA/CKAD; 70+ clusters; CAPI/CAPO; upgrades com Cilium; endurecimento de plataforma.",
    "Cluster API": "Provisionamento e ciclo de vida com CAPI/CAPO no OpenStack.",
    "Ceph": "Storage distribuído e automação de falhas de hardware.",
    "Cilium": "CNI, Hubble, policy de rede e upgrades in-place sem downtime.",
    "eBPF": "Observabilidade e rede no kernel: datapath Cilium e policy.",
    "Helm Charts": "Empacotamento no Kubernetes; padrões Helm/Kustomize com Argo.",
    "Argo Project": "CAPA: Argo CD, Workflows, Rollouts e Events; GitOps e entrega progressiva.",
    "OpenBAO": "Avaliação de segredos, rotação e alinhamento a SDLC seguro.",
    "Secure SDLC & Supply-Chain Scanning": "AppSec em escala: gitleaks, Semgrep, Checkov e Snyk; Kyverno/PSS e SecureFlag.",
    "Prometheus": "PCA na prática: PromQL, exporters, regras e Alertmanager em plataforma.",
    "Grafana": "Dashboards por data center; painéis com PromQL (PCA).",
    "Zabbix": "Monitoramento em migrações AWS e plataformas ShelfPix/Aramax.",
    "Amazon CloudWatch": "Métricas, logs, alarmes AWS; X-Ray no suporte Enterprise.",
    "Site Reliability Engineering": "ITIL, SLI/SLO, incidentes e redução de toil em escala.",
    "AWX": "Controlador Ansible com Dex; playbooks selecionados pelo bot LLM.",
    "Vim": "Editor terminal principal para SRE remoto.",
    "Zed": "Edição estruturada de código e documentação.",
    "VSCodium": "IDE sem telemetria do vendor.",
    "OTRS": "Tickets para data center e operação no varejo.",
    "MediaWiki": "Runbooks em migrações AWS.",
    "Computer Vision": "Desde 2013: OpenCV/Caffe, ShelfPix/Aramax, Android NDK.",
    "Python": "Automação, LLM, clientes Prometheus e tooling.",
    "Java": "Java EE, Maven, Hibernate/Tomcat e BI com Pentaho.",
    "C++": "Qt, Android NDK e visão embarcada junto a OpenCV.",
    "Go": "Em estudo para tooling cloud-native.",
    "Rust": "Em estudo para componentes de sistemas.",
    "Git": "Controle de versão, GitOps, Zuul e GitLab.",
    "Ansible": "Playbooks determinísticos e AWX de produção.",
    "Terraform": "Terraform, CloudFormation e Troposphere (AWS e NerdWeek).",
    "Zuul CI": "CI/CD com gates em Kubernetes e nuvem privada.",
    "GitLab CI/CD": "Pipelines e GitLab Certified Associate.",
    "AWS Messaging": "SNS, SQS e EventBridge.",
    "Slack": "Notificações, Alertmanager e bots agênticos.",
    "CoreDNS": "DNS in-cluster; alertas e runbooks.",
    "DNS & TLS": "LPIC-1, Route 53, HTTP/TLS.",
    "Large Language Models (LLM)": "Análise de alertas e stacks de modelos.",
    "Agentic AI Development": "Bot Slack com AWX, Alertmanager e playbooks Ansible.",
}

CANONICAL_SKILL_NAMES = frozenset(row[0] for row in SKILLS)


def assert_catalog_consistency() -> None:
    """Run from regenerate_skills_yaml before writing yaml."""
    missing = []
    for linkedin_name in LINKEDIN_SKILLS_FROM_CV:
        card = LINKEDIN_TO_CARD.get(linkedin_name, linkedin_name)
        if card not in CANONICAL_SKILL_NAMES:
            missing.append(f"{linkedin_name!r} → {card!r}")
    if missing:
        raise SystemExit("skills catalog: unmapped LinkedIn skills:\n  " + "\n  ".join(missing))

    if len(SKILL_BUTTONS_EN) != 9 or len(SKILL_BUTTONS_PT) != 9:  # All + 8 filters
        raise SystemExit("skills catalog: expected exactly 8 filters + All button")

    for row in SKILLS:
        name, _, categories, _, _ = row
        for slug in categories:
            if slug not in ALLOWED_CARD_CATEGORIES:
                raise SystemExit(f"skill {name!r}: invalid category {slug!r}")
        if "os" in categories and "platforms" not in categories:
            raise SystemExit(f"skill {name!r}: os-tagged cards must include platforms for navbar filter")


def skill_meta_for_linkedin(name: str) -> tuple[str, list[str], str, str] | None:
    canonical = LINKEDIN_ALIASES.get(name, name.replace("Openstack", "OpenStack"))
    for row in SKILLS:
        if row[0] == canonical:
            return row[1], row[2], row[3], row[4]
    for row in SKILLS:
        if row[0] == name:
            return row[1], row[2], row[3], row[4]
    return None