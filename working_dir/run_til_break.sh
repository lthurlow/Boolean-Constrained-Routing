#!/bin/bash 
COUNTER=1
python3.3 dijkstra.py -x -n 6 -b 2 -c -p -s $COUNTER
while [ $? -eq 0 ]; do
  echo "Using seed $COUNTER"
  python3.3 dijkstra.py -x -n 6 -b 1 -p -s $COUNTER
  COUNTER=$((COUNTER+1))
done
echo "Program failed on seed ($COUNTER)"
