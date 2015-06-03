import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os, sys
import pdb

files_to_read = []
for l in os.listdir('.'):
  if l.split('.')[-1] == 'txt':
    files_to_read.append(l)

d_l = []
d_e = []
for k in files_to_read:
  f = open(k, 'r')
  counter = 0
  temp_d = {}
  temp_e = {}
  for line in f:
    if '[' in line:
      counter = 0
      continue
    lp = line.split(',')
    if counter not in temp_d:
      temp_d[counter] = [float(lp[0].strip())]
      temp_e[counter] = [float(lp[1].strip())]
    else:
      temp_d[counter].append(float(lp[0].strip()))
      temp_e[counter].append(float(lp[1].strip()))
    counter += 1
  f.close()
  d_l.append((temp_d[1],k))
  d_e.append((temp_d[1],k))
  

counter = 0
for zzz in d_l:
  # example data
  #x = np.arange(0.1, 4, 0.5)
  x = [10,20,30,40,50]
  y1 = zzz[0]

  # First illustrate basic pyplot interface, using defaults where possible.

  plt.plot(x, y1, 'rs-.',c=plt.cm.RdYlBu(counter),label=str(zzz[1]))
  counter += 25

plt.title('Time Comparision for Shortest Path')
plt.ylabel('Time (s)')
plt.xlabel('Nodes')
lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid('on')
plt.savefig('all.png',bbox_extra_artists=(lgd,), bbox_inches='tight')
