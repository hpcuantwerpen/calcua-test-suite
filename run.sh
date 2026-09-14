# Run the CalcUA test suite on every cluster and push the results to the database.

username="${USER:-$(id -un)}"   # run on the other clusters as the current user
testdir="/apps/antwerpen/reframe/testsuite/calcua-test-suite"

usage() {
  cat <<EOF
Usage: ./run.sh [reframe options ...]

Pulls the latest calcua-test-suite (this repo), then starts
  ./run_calcua.sh --run --push-mongo <options>
detached on the login node of every cluster (leibniz, vaughan, breniac) as $username.
Nothing is printed; results end up in /apps/antwerpen/reframe/logs/.

  -h, --help   show this help

Examples:
  ./run.sh                              # default mode (calcua)
  ./run.sh --mode=daily
  ./run.sh --mode=all -t "compilation|cue"
EOF
}

for a in "$@"; do
  case "$a" in -h|--help) usage; exit 0 ;; esac
done

git -C "$testdir" pull

declare -a sites=("login1.leibniz" "login1.vaughan" "login.breniac")

# Re-quote the arguments so values like -t "compilation|cue" survive ssh + bash -c.
args=$(printf '%q ' "$@")
remote_cmd="cd $testdir; nohup ./run_calcua.sh --run --push-mongo $args > /dev/null 2>&1 &"

for n in "${sites[@]}"; do
  ssh "$username@$n" -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null \
    "bash --login -c $(printf '%q' "$remote_cmd")"
done
