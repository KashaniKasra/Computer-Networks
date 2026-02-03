# NS-2 TCP Simulation Project

This repository contains a **two-phase NS-2 (Network Simulator 2) project** focused on **TCP congestion control analysis and performance evaluation**.  
The project was developed as part of a Computer Networks course and combines simulation, trace analysis, and result visualization.

---

## Project Structure

```
NS-2/
│
├── Phase1/        # Baseline TCP congestion control simulation
├── Phase2/        # Advanced analysis and comparative experiments
│
├── README.md      # (this file)
```

Each phase is self-contained and includes its own simulation scripts, traces, analysis tools, and plots.

---

## Phase 1 – TCP Fundamentals

**Focus:**  
Understanding basic TCP congestion control behavior in NS-2.

**Key topics:**
- TCP congestion window (cwnd)
- Throughput over time
- Queue behavior and packet drops
- Trace file analysis

**Outputs:**
- Raw trace files
- Processed data
- Performance plots

Phase 1 establishes a solid baseline for TCP behavior.

---

## Phase 2 – Advanced Analysis

**Focus:**  
Comparative and automated performance evaluation.

**Key topics:**
- TCP vs UDP traffic interaction
- UDP with and without congestion control (TFRC)
- Fairness analysis
- Automated trace processing and plotting

**Outputs:**
- Multi-scenario trace files
- Comparative graphs
- Automated analysis results

Phase 2 builds directly on Phase 1 and adds deeper analytical insight.

---

## Tools & Technologies

- NS-2 Network Simulator
- TCL (simulation scripting)
- Python / AWK (trace analysis)
- GNUPlot / Matplotlib (visualization)

---

## How to Use

1. Enter the desired phase directory
2. Run the NS-2 TCL scripts
3. Analyze trace files using provided scripts
4. Review plots and results

Each phase includes a dedicated README with detailed instructions.

---

## Educational Value

This project provides practical experience with:
- TCP congestion control mechanisms
- Network simulation workflows
- Trace-based performance analysis
- Reproducible experimental design