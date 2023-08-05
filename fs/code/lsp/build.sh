#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


cd "$(dirname "$0")" || exit 1


npm install -- .
exec ./node_modules/.bin/tsc
