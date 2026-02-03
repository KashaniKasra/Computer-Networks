import os
import math
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict, namedtuple

FlowKey = namedtuple("FlowKey", ["ptype", "fid", "src", "dst"])

def parse_lines(line):
	parts = line.strip().split()

	if (len(parts) < 12):
		return None

	try:
		ev = parts[0]
		t = float(parts[1])
		frm = int(parts[2])
		to = int(parts[3])
		ptype = parts[4]
		size = int(parts[5])
		fid = int(parts[7])
		dst_addr = parts[9]
		seq = int(parts[10])
		pid = int(parts[11])

	except (ValueError, IndexError):
		return None

	try:
		dst_node = int(float(dst_addr))

	except Exception:
		dst_node = None

	return {
		"ev": ev,
		"t": t,
		"from": frm,
		"to": to,
		"fid": fid,
		"pid": pid,
		"size": size,
		"ptype": ptype,
		"dst_node_addr": dst_node,
		"seq": seq
	}

def discover_flow(trace_path, start, stop):
	flows = {}

	with open(trace_path, "r", errors="ignore") as f:
		for line in f:
			rec = parse_lines(line)

			if (not rec):
				continue

			if (rec["t"] < start or rec["t"] > stop):
				continue

			if (rec["ev"] == "+" and rec["ptype"] in ("tcp", "cbr")):
				fid = rec["fid"]
				ptype = rec["ptype"]
				src = rec["from"]
				dst = rec["dst_node_addr"]

				key = (ptype, fid)

				if (key not in flows):
					flows[key] = FlowKey(ptype=ptype, fid=fid, src=src, dst=dst)

	return flows

def analyzer(trace_path, start, stop, bin_size=0.5):
	sent_pkts = defaultdict(int)
	recv_pkts = defaultdict(int)
	sent_bytes = defaultdict(int)
	recv_bytes = defaultdict(int)

	nbins = int(math.ceil((stop - start) / bin_size)) if stop > start else 1
	recv_bytes_bins = defaultdict(lambda: [0] * nbins)

	flows_by_key = discover_flow(trace_path, start, stop)

	send_time = {}

	with open(trace_path, "r", errors="ignore") as f:
		for line in f:
			rec = parse_lines(line)

			if (not rec):
				continue

			t = rec["t"]

			if (t < start or t > stop):
				continue

			key2 = (rec["ptype"], rec["fid"])

			if (key2 not in flows_by_key):
				continue

			flow = flows_by_key[key2]

			if (rec["ev"] == "+" and rec["from"] == flow.src):
				sent_pkts[flow] += 1
				sent_bytes[flow] += rec["size"]
				send_time[(flow, rec["pid"])] = t

			if (rec["ev"] == "r"):
				if (flow.dst is None or rec["to"] == flow.dst):
					recv_pkts[flow] += 1
					recv_bytes[flow] += rec["size"]

					b = int((t - start) // bin_size)

					if (b < nbins and b >= 0):
						recv_bytes_bins[flow][b] += rec["size"]

	delay_sum = defaultdict(float)
	delay_cnt = defaultdict(int)

	with open(trace_path, "r", errors="ignore") as f:
		for line in f:
			rec = parse_lines(line)

			if (not rec):
				continue

			t = rec["t"]

			if (t < start or t > stop):
				continue

			key2 = (rec["ptype"], rec["fid"])

			if (key2 not in flows_by_key):
				continue

			flow = flows_by_key[key2]

			if (rec["ev"] == "r" and (flow.dst is None or rec["to"] == flow.dst)):
				st = send_time.get((flow, rec["pid"]))

				if (st is not None):
					delay_sum[flow] += (t - st)
					delay_cnt[flow] += 1

	duration = (stop - start) if stop > start else 1e-9

	flows_summary = {}

	for flow in flows_by_key.values():
		s_pkts = sent_pkts[flow]
		r_pkts = recv_pkts[flow]
		s_bytes = sent_bytes[flow]
		r_bytes = recv_bytes[flow]

		loss = None if s_pkts == 0 else (s_pkts - r_pkts) / s_pkts
		thr_mbps = (r_bytes * 8.0) / duration / 1e6

		avg_delay_ms = None

		if (delay_cnt[flow] > 0):
			avg_delay_ms = (delay_sum[flow] / delay_cnt[flow]) * 1000.0

		flows_summary[flow] = {
			"loss": loss,
			"throughput_mbps": thr_mbps,
			"avg_delay_ms": avg_delay_ms
		}

	bin_centers = [start + (i + 0.5) * bin_size for i in range(nbins)]

	active = [flows_summary[f]["throughput_mbps"] for f in flows_summary if flows_summary[f]["throughput_mbps"] > 1e-9]

	fairness = None

	if (len(active) >= 2):
		s = sum(active)
		s2 = sum(x * x for x in active)

		fairness = (s * s) / (len(active) * s2) if s2 > 0 else None

	return flows_summary, fairness

def plot_metrics(output_dir, results):
	os.makedirs(output_dir, exist_ok=True)

	types = list(results.keys())

	tcp_thr, udp_thr = [], []
	tcp_loss, udp_loss = [], []
	tcp_delay, udp_delay = [], []
	fairness_vals = []

	for c in types:
		flows_summary, fairness = results[c]

		tcp, udp = None, None

		for s in flows_summary:
			if s.ptype == "tcp":
				tcp = s

			elif s.ptype == "cbr":
				udp = s

		tcp_thr.append(flows_summary[tcp]["throughput_mbps"] if tcp else 0.0)
		udp_thr.append(flows_summary[udp]["throughput_mbps"] if udp else 0.0)

		tcp_loss.append((flows_summary[tcp]["loss"] * 100.0) if tcp and flows_summary[tcp]["loss"] is not None else 0.0)
		udp_loss.append((flows_summary[udp]["loss"] * 100.0) if udp and flows_summary[udp]["loss"] is not None else 0.0)

		tcp_delay.append(flows_summary[tcp]["avg_delay_ms"] if tcp and flows_summary[tcp]["avg_delay_ms"] is not None else 0.0)
		udp_delay.append(flows_summary[udp]["avg_delay_ms"] if udp and flows_summary[udp]["avg_delay_ms"] is not None else 0.0)

		fairness_vals.append(fairness if fairness is not None else 0.0)

	x = list(range(len(types)))

	width = 0.2

	plt.figure()
	plt.bar([i - width / 2 for i in x], tcp_thr, width=width, label="TCP", color="red")
	plt.bar([i + width / 2 for i in x], udp_thr, width=width, label="UDP", color="olive")
	plt.xticks(x, types)
	plt.ylabel("Throughput (Mbps)")
	plt.title("Throughput Comparison")
	plt.legend()
	plt.savefig(os.path.join(output_dir, "throughputs.png"), dpi=200)
	plt.close()

	plt.figure()
	plt.bar([i - width / 2 for i in x], tcp_loss, width=width, label="TCP", color="red")
	plt.bar([i + width / 2 for i in x], udp_loss, width=width, label="UDP", color="olive")
	plt.xticks(x, types)
	plt.ylabel("Packet Loss (%)")
	plt.title("Packet Loss Comparison")
	plt.legend()
	plt.tight_layout()
	plt.savefig(os.path.join(output_dir, "packet_losses.png"), dpi=200)
	plt.close()

	plt.figure()
	plt.bar(x, fairness_vals, color="green")
	plt.xticks(x, types)
	plt.ylabel("Jain Fairness Index")
	plt.title("Jain Fairness Index Comparison")
	plt.savefig(os.path.join(output_dir, "Jain_fairness_indexes.png"), dpi=200)
	plt.close()

	plt.figure()
	plt.bar([i - width / 2 for i in x], tcp_delay, width=width, label="TCP", color="red")
	plt.bar([i + width / 2 for i in x], udp_delay, width=width, label="UDP", color="olive")
	plt.xticks(x, types)
	plt.ylabel("Average Delay (ms)")
	plt.title("Average Delay Comparison")
	plt.legend()
	plt.savefig(os.path.join(output_dir, "average_delays.png"), dpi=200)
	plt.close()

def main():
	ap = argparse.ArgumentParser(description="Plot ns-2 metric results")

	ap.add_argument("--traces-dir", default="traces", help="Directory containing trace files")
	ap.add_argument("--out-dir", default="plots", help="Output directory for plots")
	ap.add_argument("--start", type=float, default=0.5, help="Measurement window starting time")
	ap.add_argument("--stop", type=float, default=20.0, help="Measurement window stopping time")

	args = ap.parse_args()

	traces_dir = os.path.abspath(args.traces_dir)
	out_dir = os.path.abspath(args.out_dir)

	types = {
		"tcp": os.path.join(traces_dir, "tcp.tr"),
		"udp_plain": os.path.join(traces_dir, "udp_plain.tr"),
		"udp_tfrc": os.path.join(traces_dir, "udp_tfrc.tr")
	}

	results = {}

	for cname, path in types.items():
		if (not os.path.exists(path)):
			raise FileNotFoundError(f"Trace not found: {path}")

		flows_summary, fairness = analyzer(path, args.start, args.stop)

		results[cname] = (flows_summary, fairness)

	plot_metrics(out_dir, results)

if (__name__ == "__main__"):
	main()
