#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


cd "$(dirname "$0")" || exit 1


exec node ./server.js
