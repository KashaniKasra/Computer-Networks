# Computer Networks – Course Projects

This repository contains a collection of **hands-on projects developed for the Computer Networks course**.  
Each project focuses on a core networking concept and is implemented using industry-relevant tools and protocols.

The repository is organized as **independent sub-projects**, each with its own documentation, code, and experiments.

---

## Repository Structure

```
Computer-Networks/
│
├── RDT/               # Reliable Data Transfer protocols
├── ICMP/              # ICMP Ping & Traceroute implementation
├── Distance Vector/   # Distance Vector routing simulation
└── NS-2/              # TCP congestion control simulations (Phase 1 & 2)
```

Each folder includes a dedicated `README.md` explaining the project in detail.

---

## Projects Overview

### 1. Reliable Data Transfer (RDT)
Implementation and simulation of reliable transport protocols on top of an unreliable network.

**Key concepts:**
- Stop-and-Wait / Alternating Bit protocol
- Go-Back-N (GBN)
- Checksums, timers, retransmissions

---

### 2. ICMP Ping & Traceroute
Low-level network diagnostic tools implemented using **raw sockets** and the ICMP protocol.

**Key concepts:**
- ICMP Echo Request / Reply
- RTT measurement
- TTL-based path discovery
- Traceroute logic

---

### 3. Distance Vector Routing
Simulation of the **Distance Vector routing algorithm** based on Bellman–Ford.

**Key concepts:**
- Distributed routing
- Routing table updates
- Convergence behavior
- RIP-style routing logic

---

### 4. TCP Congestion Control (NS-2)
Network simulations using **NS-2** to analyze TCP behavior under different traffic scenarios.

**Includes:**
- Phase 1: Baseline TCP congestion control analysis
- Phase 2: TCP vs UDP / TFRC comparative experiments

**Key concepts:**
- Congestion window dynamics
- Throughput and fairness
- Trace-based performance evaluation

---

## Tools & Technologies

- Python
- C
- NS-2 Network Simulator
- TCL
- Raw Sockets
- AWK / Python for trace analysis
- GNUPlot / Matplotlib

---

## Educational Goals

These projects aim to provide:
- Practical understanding of network protocols
- Experience with simulation and experimentation
- Exposure to real-world networking tools
- Clean, reproducible project structure

---

## Notes

- Each project is self-contained and can be studied independently.
- Detailed instructions and experiment results are documented inside each folder.
- The repository is intended for **academic and educational use**.

---

## Credits

- Course material inspired by *Computer Networking: A Top-Down Approach*  
  (James F. Kurose, Keith W. Ross)
