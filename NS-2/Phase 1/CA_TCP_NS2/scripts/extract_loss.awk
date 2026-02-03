# Usage: awk -f extract_loss.awk -v fid=1 input.tr > out.dat

BEGIN { bin=1.0 }

{
  if ($1 != "d") next
  if ($8 != fid) next

  t = $2
  drops[int(t/bin)] += 1
}

END {
  for (i = 0; i <= 1000; i++) {
    printf("%d %d\n", i, drops[i]+0)
  }
}
