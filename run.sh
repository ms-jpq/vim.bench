#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


cd "$(dirname "$0")" || exit 1


TAG='vim-bench'
PUBLISH_URL='https://raw.githubusercontent.com/ms-jpq/vim.bench/main/plots/'

docker buildx build --tag "$TAG" -- .
exec docker run --interactive --tty --volume "$PWD/temp:/dump" --env PUBLISH_URL="$PUBLISH_URL" -- "$TAG" "$@"
