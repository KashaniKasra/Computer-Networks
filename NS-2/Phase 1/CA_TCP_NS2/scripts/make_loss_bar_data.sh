#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
mkdir -p data

# Flow1 (fid=1) -> toNode=4
# Flow2 (fid=2) -> toNode=5
dest1=4
dest2=5

echo "#TCP  Flow1(%)  Flow2(%)" > data/loss_bar.dat

for tcp in Tahoe Reno Vegas; do
  sum1=0
  sum2=0

  for run in $(seq 1 10); do
    tr="trace/${tcp}_run${run}.tr"

    d1=$(awk '$1=="d" && $5=="tcp" && $8==1 {c++} END{print c+0}' "$tr")
    r1=$(awk -v dst="$dest1" '$1=="r" && $5=="tcp" && $8==1 && $4==dst {c++} END{print c+0}' "$tr")
    tot1=$((d1+r1))
    if [ "$tot1" -eq 0 ]; then
      lr1=0
    else
      lr1=$(awk -v d="$d1" -v t="$tot1" 'BEGIN{printf "%.6f",(d/t)*100.0}')
    fi

    d2=$(awk '$1=="d" && $5=="tcp" && $8==2 {c++} END{print c+0}' "$tr")
    r2=$(awk -v dst="$dest2" '$1=="r" && $5=="tcp" && $8==2 && $4==dst {c++} END{print c+0}' "$tr")
    tot2=$((d2+r2))
    if [ "$tot2" -eq 0 ]; then
      lr2=0
    else
      lr2=$(awk -v d="$d2" -v t="$tot2" 'BEGIN{printf "%.6f",(d/t)*100.0}')
    fi

    sum1=$(awk -v a="$sum1" -v b="$lr1" 'BEGIN{printf "%.6f",a+b}')
    sum2=$(awk -v a="$sum2" -v b="$lr2" 'BEGIN{printf "%.6f",a+b}')
  done

  avg1=$(awk -v s="$sum1" 'BEGIN{printf "%.6f",s/10.0}')
  avg2=$(awk -v s="$sum2" 'BEGIN{printf "%.6f",s/10.0}')

  echo "$tcp $avg1 $avg2" >> data/loss_bar.dat
done

echo "Wrote: data/loss_bar.dat"
