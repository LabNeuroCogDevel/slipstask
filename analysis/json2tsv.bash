#!/usr/bin/env bash
set -euo pipefail
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT

# 20200604WF - init
#    make tsv from psiturk json output
#
usage() { cat <<HEREDOC
 slips task specific tab sep val sheets from psiturk json
 USAGE: $0 psiturk.json 
 See: Makefile, fetch.bash > psiturk.json
HEREDOC
}

# checks
[ $# -ne 1 ] && usage && exit 1
[ ! -r "$1" ] && echo "ERROR: cannot read '$1'" && usage && exit 1

outdir="$(cd $(dirname "$0");pwd)/txt"

## string to header or object. DRY-up tsv creation
# add dot. comma sep names: .block, .trial_index, ...
asjq_objs(){ echo "$@"|perl -pe 's/(^| )/\1./g;s/ /, /g;'; }
astsv() { echo "subjID version $@"| perl -pe 's/ /\t/g'; }

# header
columns="block trial_index time_elapsed trial_type internal_node_id stim key_press rt outcome valued devalued cor_dir isdevalued chose score"
astsv $columns > "$outdir/task.tsv"
jq -r '
  .[0] as $v | .[1] as $r | .[1].data[] | .trialdata |
  select(.score != null) |
  [$r.workerId, $v, '"$(asjq_objs $columns)"'] |
  @tsv' < "$1" >> "$outdir/task.tsv"

# memory survey about fruit side and assocation
columns="survey_type survey_prompt correct response survey_chose survey_rt conf_rt"
astsv $columns|sed s/response/confidence/ > $outdir/fruit_survey.tsv
jq -r '
  .[0] as $v | .[1] as $r | .[1].data[] | .trialdata |
  select(.conf_rt != null) |
  [$r.workerId, $v, '"$(asjq_objs $columns)"'] |
  @tsv' < "$1" >> $outdir/fruit_survey.tsv

# misc questions about the task
columns="side_strategy pair_strategy effort misc"
astsv $columns > $outdir/feedback.tsv
jq -r '.[0] as $v | .[1] as $r | .[1].data[] | .trialdata |
  select(.responses != null) |
  .responses |fromjson|
  [$r.workerId, $v, '"$(asjq_objs $columns)"' ] |
  @tsv' < "$1" >> $outdir/feedback.tsv
