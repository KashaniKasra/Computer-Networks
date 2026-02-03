# Usage: paste run1.dat run2.dat ... run10.dat | awk -f avg10.awk > avg.dat
# Assumes each file has: time value
# paste makes: time v1 time v2 ... ; we take first time, then avg of values

{
  time=$1
  sum=0
  n=0
  # value columns are 2,4,6,...,20
  for (i=2; i<=NF; i+=2) {
    sum += $i
    n += 1
  }
  avg = (n>0)? sum/n : 0
  printf("%s %.6f\n", time, avg)
}

