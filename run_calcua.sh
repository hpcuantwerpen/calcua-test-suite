# Wrapper around reframe for the CalcUA test suite.
# Every argument except --push-mongo and -h/--help is passed to reframe unchanged.

usage() {
  cat <<'EOF'
Usage: ./run_calcua.sh [--push-mongo] [reframe options ...]

Runs the CalcUA ReFrame test suite on the current cluster: loads ReFrame/4.9.1,
points RFM_CONFIG_FILES at the calcua_config.py next to it and passes all
other arguments to reframe.

  --push-mongo   push the report to the database after the run (push_to_mongo.py)
  --mode=MODE    daily | calcua (default: excludes tags daily and massive) | all
  -h, --help     show this help (for reframe's own help: reframe -h)

Examples:
  ./run_calcua.sh --mode=all --list-tags
  ./run_calcua.sh --mode=all -l -t compilation
  ./run_calcua.sh --run --mode=all --system=vaughan:default -J reservation=myres -t "compilation|cue"
  ./run_calcua.sh --run --mode=all --system=vaughan:default -n vasp_test -P vasp_test.version=VASP/...

Output: /apps/antwerpen/reframe/logs/   Docs: README.md
EOF
}

args=()
pushtomongo=false
havemode=false

for a in "$@"; do
  case "$a" in
    -h|--help)       usage; exit 0 ;;
    --push-mongo)    pushtomongo=true ;;
    --mode|--mode=*) havemode=true; args+=("$a") ;;
    *)               args+=("$a") ;;
  esac
done

echo "Calcua run file"

if ! $havemode; then
  echo "Execution mode not specified, reverting to --mode=calcua"
  args=(--mode=calcua "${args[@]}")
fi

# the log directory is shared: files must be group-writable (group is inherited via setgid on the dirs)
umask 002

module load ReFrame/4.9.1

export RFM_CONFIG_FILES="$(dirname "$0")/calcua_config.py"
export RFM_CHECK_SEARCH_RECURSIVE=true

echo "reframe ${args[*]}"
reframe "${args[@]}"

if $pushtomongo; then
  echo 'Pushing to mongodb'
  sleep 10
  "$(dirname "$0")/push_to_mongo.py" >> /apps/antwerpen/reframe/logs/pushtomongo.logs 2>&1
fi
