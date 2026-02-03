set ns [new Simulator]
set MODE "udp_plain"
set START 0.5
set STOP 20.0
set TRACE_DIR "traces"
set NAM_DIR "nams"

file mkdir $TRACE_DIR
file mkdir $NAM_DIR

set tr [open "${TRACE_DIR}/${MODE}.tr" w]
set nam [open "${NAM_DIR}/${MODE}.nam" w]
$ns trace-all $tr
$ns namtrace-all $nam

set s_tcp [$ns node]
set s_udp [$ns node]
set r1 [$ns node]
set r2 [$ns node]
set d_tcp [$ns node]
set d_udp [$ns node]

$ns duplex-link $s_tcp $r1 10Mb 10ms DropTail
$ns duplex-link $s_udp $r1 10Mb 10ms DropTail
$ns duplex-link $r2 $d_tcp 10Mb 10ms DropTail
$ns duplex-link $r2 $d_udp 10Mb 10ms DropTail
$ns duplex-link $r1 $r2 1.5Mb 20ms DropTail
$ns queue-limit $r1 $r2 50
$ns queue-limit $r2 $r1 50

set tcp [new Agent/TCP]
$tcp set class_ 1
$ns attach-agent $s_tcp $tcp

set sink [new Agent/TCPSink]
$ns attach-agent $d_tcp $sink
$ns connect $tcp $sink

set ftp [new Application/FTP]
$ftp attach-agent $tcp

set udp [new Agent/UDP]
$udp set class_ 2
$ns attach-agent $s_udp $udp

set udpsink [new Agent/LossMonitor]
$ns attach-agent $d_udp $udpsink
$ns connect $udp $udpsink

set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set packetSize_ 1000

set udp_rate 1400000
set interval [expr {(1000.0 * 8.0) / $udp_rate}]
$cbr set interval_ $interval

proc finish {} {
	global ns tr nam sink udpsink START STOP MODE TRACE_DIR NAM_DIR

	set duration [expr {$STOP - $START}]
	if {$duration <= 0} { set duration 1e-9 }

	set tcp_bytes [$sink set bytes_]
	set tcp_thr [expr {($tcp_bytes * 8.0) / $duration / 1000000.0}]
	set udp_bytes [$udpsink set bytes_]
	set udp_thr [expr {($udp_bytes * 8.0) / $duration / 1000000.0}]
	set sum [expr {$tcp_thr + $udp_thr}]
	set num [expr {$sum * $sum}]
	set den [expr {2.0 * ($tcp_thr*$tcp_thr + $udp_thr*$udp_thr)}]

	if {$den == 0} {
		set jain 0
	} else {
		set jain [expr {$num / $den}]
	}

	puts "     MODE UDP Plain     "
	puts "TCP throughput: $tcp_thr Mbps"
	puts "UDP throughput: $udp_thr Mbps"
	puts "Jain fairness index: $jain"

	$ns flush-trace
	close $tr
	close $nam
	exit 0
}

$ns at $START "$ftp start"
$ns at $START "$cbr start"
$ns at $STOP "$ftp stop"
$ns at $STOP "$cbr stop"
$ns at [expr {$STOP + 0.1}] "finish"

$ns run
