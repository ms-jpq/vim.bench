#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar nullglob


cd "$(dirname "$0")" || exit 1


LONG_OPTS='word-len:,reps:,cache:,'

PARSED="$(getopt --options='' --longoptions="$LONG_OPTS" --name="$0" -- "$@")"
eval set -- "$PARSED"


export LSP_WORD_LEN=''
export LSP_REPS=''
export LSP_CACHE=''


while true
do
  case "$1" in
    --word-len)
      LSP_WORD_LEN="$2"
      shift
      shift
      ;;
    --reps)
      LSP_REPS="$2"
      shift
      shift
      ;;
    --cache)
      LSP_CACHE="$2"
      shift
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      >&2 printf '%s\n%s\n' '!ERR!' "$*"
      exit 2
      ;;
  esac
done
ARG_NUM=$#


if [[ "$ARG_NUM" -gt 0 ]] 
then
  >&2 printf '%s\n%s\n' '!ERR!' "$*"
  exit 2
fi


exec node ./server.js
