#!/bin/sh
# Write Artifactory .npmrc from NPM_REGISTRY and NPM_TOKEN (never commit output with real token).
set -eu

out="${1:-.npmrc}"
registry="${NPM_REGISTRY:-https://registry.npmjs.org/}"

if [ -z "${NPM_TOKEN:-}" ]; then
  echo "npmrc-from-env: NPM_TOKEN is not set" >&2
  exit 1
fi

# trim trailing slash
registry=$(printf '%s' "$registry" | sed 's:/$::')
host_path=$(printf '%s' "$registry" | sed 's#^https://##; s#^http://##')

{
  printf 'registry=%s/\n' "$registry"
  printf 'always-auth=true\n'
  printf '//%s/:_authToken=%s\n' "$host_path" "$NPM_TOKEN"
  printf '@fontsource:registry=%s/\n' "$registry"
  printf '@fortawesome:registry=%s/\n' "$registry"
} >"$out"

echo "npmrc-from-env: wrote $out for registry $registry"
