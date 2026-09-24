# Wrapper around reframe for the CalcUA test suite.
# Every argument except --push-mongo and -h/--help is passed to reframe unchanged.

usage() {
  cat <<'EOF'
Usage: ./run_calcua.sh [--push-mongo] [reframe options ...]

Runs the CalcUA ReFrame test suite on the current cluster: loads ReFrame/4.9.1,
points RFM_CONFIG_FILES at the calcua_config.py next to it and passes all
other arguments to reframe.

  --push-mongo   push the report to the database after the run (push_to_mongo.py)
  --module-mappings FILE
                 swap modules as the job script loads them; defaults to the
                 module_mappings.txt next to this script (no-op as shipped)
  --mode=MODE    daily | calcua (default: excludes tags daily and massive) | all
  -h, --help     show this help (for reframe's own help: reframe -h)

Environment:
  CALCUA_LOGDIR  where output/, stage/, performance/ and reports/ are written
                 (default: the shared /apps/antwerpen/reframe/logs; e.g. $VSC_DATA/reframe/logs)

Examples:
  ./run_calcua.sh --mode=all --list-tags
  ./run_calcua.sh --mode=all -l -t compilation
  ./run_calcua.sh --run --mode=all --system=vaughan:default -J reservation=myres -t "compilation|cue"
  ./run_calcua.sh --run --mode=all --system=vaughan:default -n vasp_test -P vasp_test.version=VASP/...

Output: $CALCUA_LOGDIR, default /apps/antwerpen/reframe/logs/   Docs: README.md
EOF
}

args=()
pushtomongo=false
havemode=false
havemapping=false

for a in "$@"; do
  case "$a" in
    -h|--help)       usage; exit 0 ;;
    --push-mongo)    pushtomongo=true ;;
    --mode|--mode=*) havemode=true; args+=("$a") ;;
    --module-mappings|--module-mappings=*)
                     havemapping=true; args+=("$a") ;;
    -p|-p*|--prgenv|--prgenv=*)
                     echo "warning: ReFrame ignores $a when --mode is set (bug, <= 4.10.3);" \
                          "use -S valid_prog_environs=ENV1,ENV2 instead" >&2
                     args+=("$a") ;;
    *)               args+=("$a") ;;
  esac
done

echo "Calcua run file"
echo "Command: reframe ${args[*]}"

if ! $havemode; then
  echo "Execution mode not specified, reverting to --mode=calcua"
  args=(--mode=calcua "${args[@]}")
fi

# module_mappings.txt next to this script is applied by default; every mapping
# in it ships commented out, so it is a no-op until someone edits it. A
# --module-mappings of your own on the command line replaces it.
map_file="$(dirname "$0")/module_mappings.txt"
if ! $havemapping && [[ -f "$map_file" ]]; then
  args=(--module-mappings "$map_file" "${args[@]}")
fi

# where reframe writes; calcua_config.py and push_to_mongo.py read the same variable
export CALCUA_LOGDIR="${CALCUA_LOGDIR:-/apps/antwerpen/reframe/logs}"

# the default log directory is shared: files must be group-writable (group is inherited via setgid on the dirs)
umask 002

module load ReFrame/4.9.1

export RFM_CONFIG_FILES="$(dirname "$0")/calcua_config.py"
export RFM_CHECK_SEARCH_RECURSIVE=true

echo "Acquiring the lock $CALCUA_LOGDIR/reframe-$VSC_INSTITUTE_CLUSTER.lock"
exec 9>"$CALCUA_LOGDIR/reframe-$VSC_INSTITUTE_CLUSTER.lock"
flock 9

reframe "${args[@]}"

if $pushtomongo; then
  echo 'Pushing to mongodb'
  sleep 10
  "$(dirname "$0")/push_to_mongo.py" >> "$CALCUA_LOGDIR/pushtomongo.logs" 2>&1
fi

flock -u 9   # optional
