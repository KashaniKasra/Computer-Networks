# expects variable: tcp (Tahoe/Reno/Vegas)
set terminal pngcairo size 1200,700
set output sprintf("plots/%s_rtt.png", tcp)

set title sprintf("RTT (ms) - %s (avg of 10 runs)", tcp)
set xlabel "Time (s)"
set ylabel "RTT (ms)"
set key top right

plot \
sprintf("data/%s_rtt_f1_avg.dat", tcp) using 1:2 with lines title sprintf("%s Flow 1 (1->5)", tcp), \
sprintf("data/%s_rtt_f2_avg.dat", tcp) using 1:2 with lines title sprintf("%s Flow 2 (2->6)", tcp)
