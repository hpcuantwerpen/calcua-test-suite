#!/bin/bash
# Run the CalcUA test suite on every cluster and push the results to the database.

testdir=/apps/antwerpen/reframe/testsuite/calcua-test-suite
logdir=${CALCUA_LOGDIR:-/apps/antwerpen/reframe/logs}
hosts=(login1.leibniz login1.vaughan login.breniac)

if [[ " $* " == *" -h "* || " $* " == *" --help "* ]]; then
  cat <<EOF
Usage: ./run.sh [reframe options ...]

Pulls this repo, starts './run_calcua.sh --run --push-mongo <options>' detached
on leibniz, vaughan and breniac, and after 5 s prints for each cluster whether
reframe is running. Output of each run: $logdir/run-<cluster>.out
(set CALCUA_LOGDIR to write elsewhere).

Examples:
  ./run.sh
  ./run.sh --mode=all -t "compilation|cue"
EOF
  exit 0
fi

git -C "$testdir" pull --recurse-submodules
git -C "$testdir" submodule update --init --recursive

# Runs on each login node. Arguments: testdir logdir logfile reframe-options...
remote_script='
cd "$1" || { echo "NOT started: no $1"; exit; }
export CALCUA_LOGDIR=$2 log=$3; shift 3
# setsid: survive the ssh logout. Its PID ($!) is also the process group of the run.
setsid nohup ./run_calcua.sh --run --push-mongo "$@" < /dev/null > "$log" 2>&1 &
pid=$!
sleep 5
if   pgrep -g $pid -f "(^|/)reframe( |$)" > /dev/null; then echo "reframe is running (pid $pid)"
elif pgrep -g $pid -x flock > /dev/null; then echo "waiting for the lock held by another run (pid $pid)"
elif pgrep -g $pid > /dev/null; then echo "started, reframe not running yet (pid $pid)"
else echo "NOT running; end of $log:"; tail -n 5 "$log" | sed "s/^/    /"
fi'

for host in "${hosts[@]}"; do
  cluster=${host#*.}   # login1.leibniz -> leibniz
  # ssh joins its arguments into one remote command line: quote them with %q
  remote_args=$(printf '%q ' "$testdir" "$logdir" "$logdir/run-$cluster.out" "$@")
  ( out=$(ssh "$host" "bash --login -s $remote_args" <<< "$remote_script") || out="NOT started (ssh failed)"
    echo "$cluster: $out" ) &
done
wait
