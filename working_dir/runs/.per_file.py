import numpy as np
import matplotlib.pyplot as plt
import os, sys
import pdb

files_to_read = []
for l in os.listdir('.'):
  if l.split('.')[-1] == 'txt':
    files_to_read.append(l)

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

  # example data
  #x = np.arange(0.1, 4, 0.5)
  y1 = temp_d[1]
  x = [10,20,30,40,50]
  y2 = temp_d[2]

  # First illustrate basic pyplot interface, using defaults where possible.

  plt.subplot(2, 1, 1)
  plt.plot(x, y1, '.-')
  plt.errorbar(x,y1,yerr=temp_e[1])
  plt.title('Time Comparision for Shortest Path')
  plt.ylabel('Boolean Time (s)')

  plt.subplot(2, 1, 2)
  plt.plot(x, y2, '.-')
  plt.errorbar(x,y2, yerr=temp_e[2])
  plt.xlabel('Nodes')
  plt.ylabel('Networkx Time (s)')

  plt.savefig(str(k).split('.')[0]+'.png')
  plt.clf()
