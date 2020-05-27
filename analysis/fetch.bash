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
[ -z "$DATABASE_URL" ] && command -v heroku && DATABASE_URL=$(heroku config:get DATABASE_URL)
[ -z "$DATABASE_URL" ] && echo "missing DATABASE_URL cannot fetch data! fix: export DATABASE_URL=\$(heroku config:get DATABASE_URL)" && exit 1

columns="block trial_index time_elapsed trial_type internal_node_id stim key_press rt outcome valued devalued cor_dir isdevalued chose score"
jsoncol=$(echo "$columns"|perl -pe 's/(^| )/\1./g;s/ /, /g;')
# .block, .trial_index, ...

# header
echo "subjID $columns" | perl -pe 's/ /\t/g'

# parse nested json
# TODO: get codeversion into jq
psql "$DATABASE_URL" -AtF$'\t' -c  'select datastring from slips' |
 jq -r '
  . as $r |
  .data[0].trialdata.responses as $q |
  .data[] |
  .trialdata |
  select(.score != null) |
  [$r.workerId, '"$jsoncol"'] |
  @tsv'
