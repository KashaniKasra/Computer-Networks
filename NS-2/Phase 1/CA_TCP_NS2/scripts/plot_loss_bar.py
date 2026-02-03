#!/usr/bin/env python3
import glob
import os
from statistics import mean
import matplotlib.pyplot as plt

TCPs = ["Tahoe", "Reno", "Vegas"]
RUNS = range(1, 11)

# destination node IDs (based on your topology/trace):
# n5 is node 4, n6 is node 5
DEST_NODE = {1: "4", 2: "5"}  # fid -> toNode

def loss_rate_for_run(trace_path: str, fid: int) -> float:
    drops = 0
    recvs = 0
    dest = DEST_NODE[fid]

    with open(trace_path, "r", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.split()
            # need at least 8 columns for fid in old trace
            if len(parts) < 8:
                continue

            event = parts[0]
            to_node = parts[3]   # column 4 (0-based index 3)
            proto = parts[4]     # column 5
            fid_col = parts[7]   # column 8

            if proto != "tcp":
                continue
            if fid_col != str(fid):
                continue

            if event == "d":
                drops += 1
            elif event == "r" and to_node == dest:
                recvs += 1

    total = drops + recvs
    if total == 0:
        return 0.0
    return (drops / total) * 100.0

def avg_loss_rate(tcp: str, fid: int) -> float:
    vals = []
    for run in RUNS:
        tr = f"trace/{tcp}_run{run}.tr"
        vals.append(loss_rate_for_run(tr, fid))
    return mean(vals)

def main():
    # compute averages
    flow1 = [avg_loss_rate(tcp, 1) for tcp in TCPs]
    flow2 = [avg_loss_rate(tcp, 2) for tcp in TCPs]

    # plot
    x = range(len(TCPs))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([i - width/2 for i in x], flow1, width, label="Flow 1")
    ax.bar([i + width/2 for i in x], flow2, width, label="Flow 2")

    ax.set_title("Average Packet Loss Rate")
    ax.set_ylabel("Loss Rate (%)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(TCPs)
    ax.legend()

    os.makedirs("plots", exist_ok=True)
    out = "plots/avg_loss_rate.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    print("Saved:", out)

if __name__ == "__main__":
    main()

