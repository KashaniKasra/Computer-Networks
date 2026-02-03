# Usage: awk -f extract_rtt.awk input_rtt.tr > out.dat
# Robust RTT extractor for ns2 rtt_ trace

BEGIN { bin=1.0 }

function isnum(x){
  return (x ~ /^-?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/)
}

{
  t=""
  v=""

  # first numeric = time
  for(i=1;i<=NF;i++){
    if(isnum($i)){ t=$i; break }
  }
  # last numeric = rtt value (seconds)
  for(i=NF;i>=1;i--){
    if(isnum($i)){ v=$i; break }
  }

  if(t=="" || v=="") next

  sum[int(t/bin)] += v
  cnt[int(t/bin)] += 1
}

END{
  for(i=0;i<=1000;i++){
    if(cnt[i]>0) ms=(sum[i]/cnt[i])*1000.0; else ms=0
    printf("%d %.6f\n", i, ms)
  }
}

