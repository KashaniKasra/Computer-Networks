set terminal pngcairo size 1200,700
set output "plots/rtt.png"
set title "RTT (ms) - 2 Flows, 3 TCP variants (avg of 10 runs)"
set xlabel "Time (s)"
set ylabel "RTT (ms)"
set key outside

plot \
"data/Tahoe_rtt_f1_avg.dat" using 1:2 with lines title "Tahoe F1 (1->5)", \
"data/Tahoe_rtt_f2_avg.dat" using 1:2 with lines title "Tahoe F2 (2->6)", \
"data/Reno_rtt_f1_avg.dat"  using 1:2 with lines title "Reno  F1 (1->5)", \
"data/Reno_rtt_f2_avg.dat"  using 1:2 with lines title "Reno  F2 (2->6)", \
"data/Vegas_rtt_f1_avg.dat" using 1:2 with lines title "Vegas F1 (1->5)", \
"data/Vegas_rtt_f2_avg.dat" using 1:2 with lines title "Vegas F2 (2->6)"

