# TCP Performance Analysis using NS-2  
**Phase 2 – Advanced Experiments and Comparative Analysis**

This repository contains **Phase 2 of the NS-2 TCP simulation project**, building directly on the baseline simulations developed in Phase 1.  
The focus of this phase is **deeper performance analysis and comparison of different traffic types and scenarios**, using trace-based evaluation.

---

## Project Overview

In Phase 2, multiple simulation scenarios are executed to analyze how TCP behaves under different network conditions and in the presence of competing traffic (e.g., UDP).  
The experiments emphasize **quantitative analysis**, automation, and comparison across scenarios.

Key objectives include:
- Comparing TCP performance under different workloads
- Studying fairness between TCP and UDP flows
- Analyzing throughput, delay, and congestion behavior
- Automating trace analysis and plotting

---

## Directory Structure

```
CA_TCP_NS2/
│
├── nams/            # NAM visualization output files
├── plots/           # Generated graphs from experiments
├── traces/          # Raw NS-2 trace files
│
├── tcp.tcl          # TCP-based simulation scenario
├── udp_plain.tcl    # Baseline UDP traffic scenario
├── udp_tfrc.tcl     # UDP with TFRC congestion control
│
├── trace_analyze.py # Trace parsing and metric extraction
└── plot_all.py      # Automated plotting of all results
```

### Folder Descriptions

- **traces/**  
  Contains detailed event-level trace files produced by NS-2 for each experiment.

- **nams/**  
  Network Animator (NAM) output files for visual inspection of packet flows.

- **plots/**  
  Final graphs illustrating performance metrics such as throughput and fairness.

---

## Simulation Scenarios

Phase 2 includes multiple TCL-based scenarios:

### 1. TCP Scenario (`tcp.tcl`)
- Standard TCP flow
- Used as a reference baseline
- Evaluates congestion window dynamics and throughput

### 2. UDP Plain (`udp_plain.tcl`)
- UDP traffic without congestion control
- Demonstrates aggressive bandwidth usage
- Highlights fairness issues when competing with TCP

### 3. UDP TFRC (`udp_tfrc.tcl`)
- UDP with TCP-Friendly Rate Control (TFRC)
- Designed to coexist fairly with TCP
- Allows direct comparison with plain UDP behavior

---

## Trace Analysis

Trace files are processed using Python scripts:

- **`trace_analyze.py`**
  - Parses NS-2 trace files
  - Extracts metrics such as:
    - Throughput
    - Packet loss
    - Timing information

- **`plot_all.py`**
  - Automates plot generation
  - Produces consistent visualizations across scenarios

Extracted data is used to compare protocol behavior objectively.

---

## How to Run

### 1. Run Simulations

```bash
ns tcp.tcl
ns udp_plain.tcl
ns udp_tfrc.tcl
```

Each run generates corresponding trace and NAM files.

---

### 2. Analyze Traces

```bash
python trace_analyze.py
```

This script processes trace files and prepares data for visualization.

---

### 3. Generate Plots

```bash
python plot_all.py
```

All resulting graphs are saved in the `plots/` directory.

---

## Metrics Evaluated

Typical metrics analyzed in Phase 2:

- Throughput over time
- Bandwidth fairness
- Packet drop behavior
- Impact of UDP traffic on TCP performance

These metrics enable clear comparison between different congestion control approaches.

---

## Design Assumptions

- Wired topology
- DropTail queue discipline
- Fixed simulation duration
- No wireless or mobility effects
- Deterministic experiment setup

---

## Phase 2 vs Phase 1

| Phase 1 | Phase 2 |
|-------|--------|
| Basic TCP simulation | Multi-scenario experiments |
| Manual analysis | Automated trace analysis |
| Single flow focus | TCP vs UDP comparisons |
| Introductory | Analytical & comparative |

---

## Educational Value

Phase 2 strengthens understanding of:
- TCP friendliness and fairness
- Congestion control interactions
- Trace-driven performance evaluation
- Reproducible networking experiments