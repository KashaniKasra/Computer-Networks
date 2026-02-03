set ns [new Simulator]
set MODE "tcp"
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
set r1 [$ns node]
set r2 [$ns node]
set d_tcp [$ns node]

$ns duplex-link $s_tcp $r1 10Mb 10ms DropTail
$ns duplex-link $r2 $d_tcp 10Mb 10ms DropTail
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

proc finish {} {
	global ns tr nam sink START STOP TRACE_DIR NAM_DIR MODE

	set bytes [$sink set bytes_]
	set duration [expr {$STOP - $START}]
	if {$duration <= 0} { set duration 1e-9 }

	set thr_mbps [expr {($bytes * 8.0) / $duration / 1000000.0}]

	puts "     MODE TCP     "
	puts "TCP throughput: $thr_mbps Mbps"

	$ns flush-trace
	close $tr
	close $nam
	exit 0
}

$ns at $START "$ftp start"
$ns at $STOP "$ftp stop"
$ns at [expr {$STOP + 0.1}] "finish"

$ns run
