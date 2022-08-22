#!/usr/bin/env bash
set -euo pipefail
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT

#
# 20200527WF/FC - init
#   fetch data from DB
#   uses DATABASE_URL, or heroku to fetch
#

# check/try to fetch database location
DATABASE_URL="$($(dirname $0)/dburl)"
[ -z "$DATABASE_URL" ] && exit 1
# parse nested json. add coversion like ["codeversion", datastring]|
psql "$DATABASE_URL" -AtF$'\t' -c  "select '[\"'||codeversion||'\",'||datastring||']' from slips"

