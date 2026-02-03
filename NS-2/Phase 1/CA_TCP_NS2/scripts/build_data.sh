#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

mkdir -p data/tmp

TCPs=("Tahoe" "Reno" "Vegas")
FIDS=(1 2)

# 1) per-run extraction
for tcp in "${TCPs[@]}"; do
  for run in $(seq 1 10); do
    tr="trace/${tcp}_run${run}.tr"

    # Throughput per flow
    for fid in "${FIDS[@]}"; do
      awk -f scripts/extract_throughput.awk -v fid=$fid "$tr" > "data/tmp/${tcp}_thr_f${fid}_run${run}.dat"
      awk -f scripts/extract_loss.awk       -v fid=$fid "$tr" > "data/tmp/${tcp}_loss_f${fid}_run${run}.dat"
    done

    # RTT per flow
    awk -f scripts/extract_rtt.awk "trace/${tcp}_rtt_f1_run${run}.tr" > "data/tmp/${tcp}_rtt_f1_run${run}.dat"
    awk -f scripts/extract_rtt.awk "trace/${tcp}_rtt_f2_run${run}.tr" > "data/tmp/${tcp}_rtt_f2_run${run}.dat"
  done
done

# 2) average over 10 runs
for tcp in "${TCPs[@]}"; do
  for fid in "${FIDS[@]}"; do
    paste data/tmp/${tcp}_thr_f${fid}_run*.dat  | awk -f scripts/avg10.awk > data/${tcp}_thr_f${fid}_avg.dat
    paste data/tmp/${tcp}_loss_f${fid}_run*.dat | awk -f scripts/avg10.awk > data/${tcp}_loss_f${fid}_avg.dat
    paste data/tmp/${tcp}_rtt_f${fid}_run*.dat  | awk -f scripts/avg10.awk > data/${tcp}_rtt_f${fid}_avg.dat
  done
done

echo "Done. Averaged data files are in ./data"
