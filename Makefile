.PHONY: clean docker-push help image secrets shell

DOCKER_IMG_NAME ?= hugo
DOCKER_IMG_TAG ?= latest
DOCKER_NAMESPACE ?= gohugo.io

WORKDIR=$(PWD)

HUGO_CMD=docker run --rm -it -v ${WORKDIR}:/site ${DOCKER_NAMESPACE}/${DOCKER_IMG_NAME}:${DOCKER_IMG_TAG}
HUGO_SERVER=docker run --rm -it -p1313:1313 -v ${WORKDIR}:/site ${DOCKER_NAMESPACE}/${DOCKER_IMG_NAME}:${DOCKER_IMG_TAG}

DATE=$(date)
COMMIT_MESSAGE="2021 community return effort ${DATE}"
VENDOR ?= ${WORKDIR}/vendor

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

image: $(VENDOR) ## Build gohugo.io/hugo docker image
	cd ${VENDOR}; git pull
	cd ${VENDOR}; docker build --build-arg HUGO_BUILD_TAGS=extended -t ${DOCKER_NAMESPACE}/${DOCKER_IMG_NAME}:${DOCKER_IMG_TAG} .

deploy: ## Deploy the post to production
	${HUGO_CMD} -t hello-friend-ng
	cd public
	git add .
	git commit -m ${COMMIT_MESSAGE}
	git push origin master

local: image ## Run gohugo.io/hugo binding 0.0.0.0
	rm -rf public/*
	${HUGO_CMD} -t hello-friend-ng
	${HUGO_SERVER} server -D --bind 0.0.0.0 

post: image ## Create a new post usage: make post post=title-of-my-post
	${HUGO_CMD} new posts/${post}

$(VENDOR):
	@ mkdir -p $(VENDOR)
	git clone https://github.com/gohugoio/hugo.git ${VENDOR}
