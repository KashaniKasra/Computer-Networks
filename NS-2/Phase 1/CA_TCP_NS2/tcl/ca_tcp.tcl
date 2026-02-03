# Usage: ns ca_tcp.tcl <TCPType> <seed> <runId>
# TCPType: Tahoe | Reno | Vegas

set tcpType [lindex $argv 0]
set seed    [lindex $argv 1]
set runId   [lindex $argv 2]

# -------- Simulator --------
set ns [new Simulator]

# RNG seed
ns-random $seed

# -------- Trace files --------
set trfile [open "trace/${tcpType}_run${runId}.tr" w]
$ns trace-all $trfile

# RTT trace per flow
set rtt1 [open "trace/${tcpType}_rtt_f1_run${runId}.tr" w]
set rtt2 [open "trace/${tcpType}_rtt_f2_run${runId}.tr" w]

# -------- Nodes --------
set n1 [$ns node]
set n2 [$ns node]
set r1 [$ns node]
set r2 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

# -------- Global settings required by project --------
# TCP payload size = 1000 bytes
Agent/TCP set packetSize_ 1000

# -------- Links --------
# n1 - r1 : 100Mb, 5ms
$ns duplex-link $n1 $r1 100Mb 5ms DropTail

# n2 - r1 : 100Mb, variable delay (we'll set initial then vary)
$ns duplex-link $n2 $r1 100Mb 5ms DropTail

# r1 - r2 : 100kb, 1ms
$ns duplex-link $r1 $r2 100Kb 1ms DropTail

# r2 - n5 : 100Mb, 5ms
$ns duplex-link $r2 $n5 100Mb 5ms DropTail

# r2 - n6 : 100Mb, variable delay
$ns duplex-link $r2 $n6 100Mb 5ms DropTail

# Queue size in routers = 10 packets
# (DropTail queue limit)
$ns queue-limit $n1 $r1 10
$ns queue-limit $n2 $r1 10
$ns queue-limit $r1 $r2 10
$ns queue-limit $r2 $n5 10
$ns queue-limit $r2 $n6 10

# -------- Random variable delay: Uniform(5,25) ms --------
set rv [new RandomVariable/Uniform]
$rv set min_ 5
$rv set max_ 25

proc update_delay {ns rv a b} {
    # pick random delay in ms
    set d [expr [$rv value]]
    # set both directions delay
    set linkAB [$ns link $a $b]
    set linkBA [$ns link $b $a]
    $linkAB set delay_ "${d}ms"
    $linkBA set delay_ "${d}ms"
}

# schedule delay changes randomly
for {set t 0} {$t <= 1000} {incr t 1} {
    $ns at $t "update_delay $ns $rv $n2 $r1"
    $ns at $t "update_delay $ns $rv $r2 $n6"
}
# -------- TCP Agents (2 flows) --------

# Flow 1: n1 -> n5
if {$tcpType == "Vegas"} {
    set tcp1 [new Agent/TCP/Vegas]
} else {
    set tcp1 [new Agent/TCP]
}
$tcp1 set fid_ 1
$tcp1 set ttl_ 64
$ns attach-agent $n1 $tcp1

set sink1 [new Agent/TCPSink]
$ns attach-agent $n5 $sink1
$ns connect $tcp1 $sink1

if {$tcpType == "Tahoe"} {
    $tcp1 set tcpVariant_ Tahoe
} elseif {$tcpType == "Reno"} {
    $tcp1 set tcpVariant_ Reno
}

$tcp1 tracevar rtt_
$tcp1 attach $rtt1

set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1

# Flow 2: n2 -> n6
if {$tcpType == "Vegas"} {
    set tcp2 [new Agent/TCP/Vegas]
} else {
    set tcp2 [new Agent/TCP]
}
$tcp2 set fid_ 2
$tcp2 set ttl_ 64
$ns attach-agent $n2 $tcp2

set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2

if {$tcpType == "Tahoe"} {
    $tcp2 set tcpVariant_ Tahoe
} elseif {$tcpType == "Reno"} {
    $tcp2 set tcpVariant_ Reno
}

$tcp2 tracevar rtt_
$tcp2 attach $rtt2

set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2


# Start both flows at time 0
$ns at 0.0 "$ftp1 start"
$ns at 0.0 "$ftp2 start"

# Stop at 1000 seconds
$ns at 1000.0 "finish"

proc finish {} {
    global ns trfile rtt1 rtt2
    $ns flush-trace
    close $trfile
    close $rtt1
    close $rtt2
    exit 0
}

$ns run
