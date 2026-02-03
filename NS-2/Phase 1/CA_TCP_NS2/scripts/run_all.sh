#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

mkdir -p trace data plots

TCPs=("Tahoe" "Reno" "Vegas")

# 10 runs, each 1000s
for tcp in "${TCPs[@]}"; do
  for run in $(seq 1 10); do
    seed=$((1000 + run)) 
    echo "Running $tcp run $run (seed=$seed)"
    ns tcl/ca_tcp.tcl "$tcp" "$seed" "$run"
  done
done
