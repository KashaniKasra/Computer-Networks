# expects variable: tcp (Tahoe/Reno/Vegas)
set terminal pngcairo size 1200,700
set output sprintf("plots/%s_loss_zoom50.png", tcp)

set title sprintf("Packet Drops per Second - %s (avg of 10 runs) [0-50s]", tcp)
set xlabel "Time (s)"
set ylabel "Drops / second"
set key top right
set xrange [0:50]
set yrange [0:1]

plot \
sprintf("data/%s_loss_f1_avg.dat", tcp) using 1:2 with lines title sprintf("%s Flow 1 (1->5)", tcp), \
sprintf("data/%s_loss_f2_avg.dat", tcp) using 1:2 with lines title sprintf("%s Flow 2 (2->6)", tcp)
