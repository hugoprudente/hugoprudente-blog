#!/bin/sh
set -e
cd /project

# node_modules baked into the image; copy once per volume (no host npm).
if [ ! -f node_modules/.from-toha-image ]; then
  rm -rf node_modules
  cp -a /npm/node_modules /project/node_modules
  touch node_modules/.from-toha-image
fi

if [ "$1" = "build" ]; then
  shift
  exec hugo build --config hugo.yaml --minify "$@"
fi

exec hugo server -D --config hugo.yaml --bind 0.0.0.0 --baseURL http://localhost:1313/ --disableFastRender "$@"
