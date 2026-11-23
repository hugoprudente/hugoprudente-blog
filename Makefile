.PHONY: help serve serve-toha stop build build-toha regenerate-skills post


WORKDIR=$(PWD)



define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-30s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

serve: ## hello-friend-ng dev server (config.toml)
	podman compose up hugo

serve-toha: ## Toha dev server (builds image; npm only inside container)
	podman compose --profile toha up hugo-toha --build

stop: ## Stop compose services
	podman compose --profile toha down
	podman compose down

build: ## Build hello-friend-ng into ./public
	podman run --rm -v ${WORKDIR}:/project:Z -w /project ghcr.io/gohugoio/hugo:latest build --config config.toml

build-toha: ## Build Toha into ./public (loads .env for Artifactory npm)
	@set -a && [ -f .env ] && . ./.env; set +a; \
	podman build -f Containerfile.toha \
	  --build-arg NPM_TOKEN="$$NPM_TOKEN" \
	  --build-arg NPM_REGISTRY="$$NPM_REGISTRY" \
	  -t hugoprudente-blog-toha:latest .
	podman run --rm -v ${WORKDIR}:/project:Z hugoprudente-blog-toha:latest build

build-toha-prod: ## Toha build with production baseURL
	@set -a && [ -f .env ] && . ./.env; set +a; \
	podman build -f Containerfile.toha \
	  --build-arg NPM_TOKEN="$$NPM_TOKEN" \
	  --build-arg NPM_REGISTRY="$$NPM_REGISTRY" \
	  -t hugoprudente-blog-toha:latest .
	podman run --rm -v ${WORKDIR}:/project:Z hugoprudente-blog-toha:latest build -b https://hugoprudente.github.io/

verify-toha-ui: ## Host Python Playwright (headed); run make serve-toha first
	python3 scripts/verify_toha_home.py --headed --pause --base-url http://127.0.0.1:1313/en/

verify-toha-ui-headless: ## Same checks, no browser window
	python3 scripts/verify_toha_home.py --headless --base-url http://127.0.0.1:1313/en/

regenerate-skills: ## Rewrite data/*/sections/skills.yaml from scripts/skills_catalog.py
	python3 scripts/regenerate_skills_yaml.py

post: ## Create a new post usage: make post post=title-of-my-post
	podman run --rm -v ${WORKDIR}:/project:Z -w /project ghcr.io/gohugoio/hugo:latest new posts/${post}/index.en.md
