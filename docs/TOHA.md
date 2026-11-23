# Toha theme (`feat/toha` branch)

Theme source: [hugo-themes/toha](https://github.com/hugo-themes/toha) in `third_party/toha` (Go `replace` in `go.mod`).

## Commands

| Make target | Config | Theme |
|-------------|--------|-------|
| `make serve` | `config.toml` | hello-friend-ng |
| `make build` | default | hello-friend-ng |
| `make serve-toha` | `hugo.yaml` | Toha module |
| `make build-toha` | `hugo.yaml` | Toha module |

**No `npm` on the host.** `Containerfile.toha` runs `npm ci` during `podman build`; the entrypoint copies `node_modules` into the mounted project once.

### npm (public default; private registry optional)

1. Copy [`.env.example`](../.env.example) to `.env` (`.env` is gitignored).
2. Default `NPM_REGISTRY` is [public npm](https://registry.npmjs.org/). Set `NPM_TOKEN` / a private `NPM_REGISTRY` in `.env` only if you need a mirror.
3. Run `make serve-toha` or `make build-toha` — compose/Makefile pass build-args from `.env`; **never commit `.env` or `.npmrc`**.

CI uses GitHub secrets `NPM_TOKEN` and `NPM_REGISTRY` with [`scripts/npmrc-from-env.sh`](../scripts/npmrc-from-env.sh) when a private registry is required.

`npm ci --omit=dev` skips ESLint-only deps (e.g. `yocto-queue@0.1.0`). Theme runtime packages live in `package.json` `dependencies`. If a new 404 appears, cache that package on your registry or move it to `dependencies`—do not substitute other versions (e.g. `yocto-queue@1.2.2` for `0.1.0`) without upgrading the parent package.

### Local-only files

- **`profile_parsed.json`** — keep outside the repo or rely on gitignore; point `LINKEDIN_PROFILE` at `~/tmp/linkedin/...` when running `linkedin_to_toha.py`.

## Speaking and Writing

- Home **Speaking** lists posts with `speaking: true` in front matter (`event`, `youtube` optional).
- **Writing** / **Artigos** is the navbar label; content stays under `/posts/` (technical posts should **not** set `speaking: true`).
- **Skills** — canonical list in `scripts/skills_catalog.py`; **`make regenerate-skills`** writes `data/*/sections/skills.yaml`. Section is **disabled** on home/nav (`SKILLS_SECTION_ENABLED = False` in the catalog); set it `True` and regen when ready (weight `11` = last section). See [docs/skills-taxonomy.md](skills-taxonomy.md). LinkedIn sync updates filter buttons only (cards come from regen; unmapped endorsements log a warning).
- **Certifications** section (`data/*/sections/accomplishments.yaml`) — org links go to **exam/training pages** (not vendor homepages); badges under `assets/images/sections/certifications/` via `scripts/fetch_cert_badge_images.py` + `scripts/normalize_cert_badges.py` (see that folder’s README). LinkedIn sync preserves hand-tuned `image` / `organization.url` / `certificateURL`.
- Legacy embed index: `online-talks-and-lectures-archive`.

## LinkedIn profile sync

After you export or fetch a new `profile_parsed.json` (see `~/tmp/linkedin`):

```bash
export LINKEDIN_PROFILE=~/tmp/linkedin/export/live-2026-11-11/profile_parsed.json
export LINKEDIN_PHOTO=~/tmp/linkedin/1714759018041.jpeg   # optional
python3 scripts/linkedin_to_toha.py
```

Use `--lang en`, `--dry-run`, or `--skip-photo` as needed. **About:** LinkedIn sync updates EN `summary` from the export; **pt-br About keeps the existing `summary`** in `data/pt-br/sections/about.yaml` on regen (full PT-BR copy). Default PT text lives in `ABOUT_SUMMARY_PT` in the script when the file is new. pt-br hero bullets are translated; experience bullets stay English until you request full translation.

## Files

- `hugo.yaml` — Toha site config
- `data/en` and `data/pt-br` — home page sections
- `layouts/partials/helpers/get-sass-options.html` — Dart Sass transpiler
- `layouts-hello-friend-ng/` — old theme overrides (not used by Toha)

## Production

```bash
make build-toha-prod
```

Then publish `public/` to the `hugoprudente.github.io` submodule as today.

Production Toha builds use `hugo build --minify`. Check GA4 (`G-G73E6NWXR0`) in generated HTML. After deploy, run [PageSpeed Insights](https://pagespeed.web.dev/analysis/) on `https://hugoprudente.github.io/en/` and address LCP/CLS issues (image sizes, third-party JS).

### Markdown on posts

`hugo.yaml` enables **Mermaid** (`{{< mermaid >}}`), **KaTeX** (`math: true` / `$$`), and **highlight.js** on posts.

### UI check (host Python Playwright)

Uses your **host** `pip install playwright` — **not** npm inside the Toha container.

```bash
# one-time on the laptop (not in the image)
playwright install chromium

# terminal A
make serve-toha

# terminal B — opens Chromium, scroll the home page, then press Enter
make verify-toha-ui

# CI / quick check without a window
make verify-toha-ui-headless
```

Script: [`scripts/verify_toha_home.py`](../scripts/verify_toha_home.py) (navbar, Certifications badges/org links, Skills filters when enabled, GA4 id).
