set ns [new Simulator]
set MODE "udp_tfrc"
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

set T 0.2 ;
set rate 300000 ;
set minRate 50000 ;
set maxRate 2000000 ;
set last_nlost 0
set last_npkts 0

proc rate_to_interval {rate_bps pktSizeBytes} {
	return [expr {($pktSizeBytes * 8.0) / $rate_bps}]
}

proc apply_rate {} {
	global rate minRate maxRate cbr

	if {$rate < $minRate} { set rate $minRate }
	if {$rate > $maxRate} { set rate $maxRate }

	set pktSize [$cbr set packetSize_]
	set interval [rate_to_interval $rate $pktSize]

	$cbr set interval_ $interval
}

proc control_udp_rate {} {
	global ns T rate udpsink last_nlost last_npkts

	set has_nlost 1
	if {[catch {$udpsink set nlost_} nlost_now]} {
		set has_nlost 0
	}

	set loss 0
	if {$has_nlost == 1} {
		if {$nlost_now > $last_nlost} {
			set loss 1
		}
		set last_nlost $nlost_now
	} else {
		set npkts_now [$udpsink set npkts_]
		if {$npkts_now == $last_npkts} {
			set loss 1
		}
		set last_npkts $npkts_now
	}

	if {$loss == 1} {
		set rate [expr {$rate * 0.85}]
	} else {
		set rate [expr {$rate + 0.01 * $rate}]
	}

	apply_rate

	$ns at [expr {[$ns now] + $T}] "control_udp_rate"
}

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

	set udp_loss_str "UDP loss Error"
	if {![catch {$udpsink set nlost_} nlost_now]} {
		set udp_loss_str "UDP nlost_: $nlost_now"
	}

	puts "     MODE UDP TFRC     "
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
apply_rate
$ns at [expr {$START + 0.2}] "control_udp_rate"
$ns at $STOP "$ftp stop"
$ns at $STOP "$cbr stop"
$ns at [expr {$STOP + 0.1}] "finish"

$ns run
