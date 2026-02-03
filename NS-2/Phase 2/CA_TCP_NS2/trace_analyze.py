import argparse
from collections import defaultdict
from typing import Tuple

FlowKey = Tuple[str, int, int, int]

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
		src = int(float(parts[8]))
		dst = int(float(parts[9]))
		seq = int(parts[10])

	except (ValueError, IndexError):
		return None

	return {
		"ev": ev,
		"t": t,
		"from": frm,
		"to": to,
		"fid": fid,
		"size": size,
		"ptype": ptype,
		"src": src,
		"dst": dst,
		"seq": seq
	}

def analyzer(trace_path, start, stop):
	sent_pkts = defaultdict(int)
	recv_pkts = defaultdict(int)
	recv_bytes = defaultdict(int)
	send_time = defaultdict(dict)
	delays = defaultdict(list)

	with open(trace_path, "r", errors="ignore") as f:
		for line in f:
			rec = parse_lines(line)
			
			if (not rec):
				continue
			
			if (rec["t"] < start or rec["t"] > stop):
				continue

			fid = rec["fid"]
			ptype = rec["ptype"]
			src = rec["src"]
			dst = rec["dst"]
			size = rec["size"]

			if ((ptype == "ack") or (ptype == "tcp" and size <= 40)):
				continue

			key = (ptype, fid, src, dst)

			if (rec["ev"] == "-" and rec["from"] == src):
				sent_pkts[key] += 1
				send_time[key][rec["seq"]] = rec["t"]

			if (rec["ev"] == "r" and rec["to"] == dst):
				recv_pkts[key] += 1
				recv_bytes[key] += size

				st = send_time[key].get(rec["seq"])

				if (st is not None):
					delays[key].append(rec["t"] - st)

		duration = stop - start if stop > start else 1e-9

		all_keys = sorted(set(list(sent_pkts.keys()) + list(recv_pkts.keys())))

		results = {}

		for key in all_keys:
			ptype, fid, src, dst = key

			thr_mbps = (recv_bytes[key] * 8.0) / duration / 1e6
			loss = None if sent_pkts[key] == 0 else (1.0 - (recv_pkts[key] / sent_pkts[key]))
			avg_delay_ms = None

			if (delays[key]):
				avg_delay_ms = (sum(delays[key]) / len(delays[key])) * 1000.0

			results[key] = {
				"ptype": ptype,
				"fid": fid,
				"src": src,
				"dst": dst,
				"sent": sent_pkts[key],
				"recv": recv_pkts[key],
				"loss": loss,
				"throughput_mbps": thr_mbps,
				"avg_delay_ms": avg_delay_ms,
				"delay_samples": len(delays[key])
			}

		thrs = [v["throughput_mbps"] for v in results.values() if v["throughput_mbps"] > 0]

		jain = None

		if (len(thrs) >= 2):
			num = (sum(thrs) ** 2)
			den = len(thrs) * sum(x * x for x in thrs)

			jain = (num / den) if den > 0 else None

		return results, jain

def main():
	ap = argparse.ArgumentParser(description="Analyze ns-2 trace")

	ap.add_argument("trace", help="Path to trace file")
	ap.add_argument("--start", type=float, default=0.5, help="Measurement window starting time")
	ap.add_argument("--stop", type=float, default=20.0, help="Measurement window stopping time")

	args = ap.parse_args()

	results, jain = analyzer(args.trace, args.start, args.stop)

	print(f"\nResults of {args.trace}:     ")
	print(f"   Window: {args.start} .. {args.stop} (duration={max(args.stop-args.start, 0):.2f} sec)")

	for (ptype, fid, src, dst), v in results.items():
		if (ptype == "cbr"):
			ptype = "UDP"
		elif (ptype == "tcp"):
			ptype = "TCP"

		print(f"\n   Flow {ptype}:")

		print(f"      - Throughput = {v['throughput_mbps']:.4f} Mbps")

		if (v["loss"] is not None):
			print(f"      - Packet Loss = {v['loss']:.4f}% (sent={v['sent']}, recv={v['recv']})")
		else:
			print(f"      - Packet Loss = Error (sent={v['sent']}, recv={v['recv']})")

		if (v["avg_delay_ms"] is not None):
			print(f"      - Average Delay = {v['avg_delay_ms']:.4f} ms")
		else:
			print("      - Average Delay = Error")

	if (jain is not None):
		print(f"\n   Jain Fairness Index = {jain:.4f}")

if (__name__ == "__main__"):
	main()
