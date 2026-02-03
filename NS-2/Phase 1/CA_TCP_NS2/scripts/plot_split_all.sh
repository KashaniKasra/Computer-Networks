#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

# sanity check: data files must exist
for tcp in Tahoe Reno Vegas; do
  for f in "thr_f1" "thr_f2" "rtt_f1" "rtt_f2" "loss_f1" "loss_f2"; do
    file="data/${tcp}_${f}_avg.dat"
    if [ ! -f "$file" ]; then
      echo "Missing: $file"
      exit 1
    fi
  done
done

for tcp in Tahoe Reno Vegas; do
  echo "Plotting $tcp..."
  gnuplot -e "tcp='$tcp'" plots/plot_one_throughput.gp
  gnuplot -e "tcp='$tcp'" plots/plot_one_rtt.gp
  gnuplot -e "tcp='$tcp'" plots/plot_one_loss.gp
done

echo "Done. Created 9 plots in ./plots"
