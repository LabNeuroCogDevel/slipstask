#!/usr/bin/env bash
set -euo pipefail
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT

#
# 20200527WF/FC - init
#   fetch data from DB
#   uses DATABASE_URL, or heroku to fetch
#

# check/try to fetch database location
! env| grep -q ^DATABASE_URL= && DATABASE_URL=""
[ -z "$DATABASE_URL" ] && command -v heroku >/dev/null && DATABASE_URL=$(heroku config:get DATABASE_URL)
[ -z "$DATABASE_URL" ] && echo "missing DATABASE_URL cannot fetch data! fix: export DATABASE_URL=\$(heroku config:get DATABASE_URL)" && exit 1
# parse nested json. add coversion like ["codeversion", datastring]|
psql "$DATABASE_URL" -AtF$'\t' -c  "select '[\"'||codeversion||'\",'||datastring||']' from slips"

