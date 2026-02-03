#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

for tcp in Tahoe Reno Vegas; do
  echo "Plotting ZOOM50 for $tcp..."
  gnuplot -e "tcp='$tcp'" plots/plot_one_throughput_zoom50.gp
  gnuplot -e "tcp='$tcp'" plots/plot_one_rtt_zoom50.gp
  gnuplot -e "tcp='$tcp'" plots/plot_one_loss_zoom50.gp
done

echo "Done. Created 9 zoom(0-50s) plots in ./plots"
