set terminal pngcairo size 1200,700
set output "plots/avg_loss_rate.png"

set title "Average Packet Loss Rate"
set ylabel "Loss Rate (%)"

set style data histograms
set style histogram clustered gap 1
set style fill solid 1.0 border -1
set boxwidth 0.9

set grid ytics
set key top right

plot "data/loss_bar.dat" using 2:xtic(1) title "Flow 1", \
     "" using 3 title "Flow 2"
