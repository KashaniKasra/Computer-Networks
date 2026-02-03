# Usage: awk -f extract_throughput.awk -v fid=1 input.tr > out.dat
# Columns:
# $1=event, $2=time, $6=pkt_size(bytes), $8=fid

BEGIN { bin=1.0 }

{
  if ($1 != "r") next       
  if ($8 != fid) next        

  t = $2
  size = $6                    
  bytes[int(t/bin)] += size
}

END {
  for (i = 0; i <= 1000; i++) {
    mbps = (bytes[i] * 8.0) / (1e6 * bin)
    printf("%d %.6f\n", i, mbps)
  }
}
