import os, sys
import subprocess
import getopt
import pdb
import math

def average(s): return sum(s) * 1.0 / len(s)

def print_args():
  print("STATS using Dijkstra Shortest Path:")
  print("h:\tprints this menu.")
  print("v:\tprints logging information.")
  print("n:\t-n [10] graph uses 10 vertices/nodes.")
  print("d:\t-d [3] each vertice on averages has 3 neighbors.")
  print("s:\t-s [100] seeds the random number generator.")
  print("t:\t-t ['pyeda'] uses pyeda module to select boolean expressions.")
  print("b:\t-b [4] indicates 4 boolean variables will be used.")
  print("f:\t-f ['output.txt'] saves output to a file.")
  print("c:\tcompares against networkx dijkstra run time.")
  print("e:\tsets the graph to have bi-directional links with equal values.")
  print("p:\tturns on policy based routing protol, defaults to dijkstra")
  print("")


if __name__ == "__main__":
  #dijkstra.py -e -p -b 4 -x -n 16 -d 15
  user_input = []
  file_name = "default.txt"
  try:
    opts, args = getopt.getopt(sys.argv[1:], "n:d:s:t:b:ph", ["help"])
  except getopt.GetoptError:
    print_args()
    sys.exit(1)
  for o, a in opts:
    #logging.debug('option: %s, argument: %s' % (o,a))
    if o in ("-h", "--help"):
      print_args()
      exit(0)
    elif o in "-n":
      user_input.append("-n %d" % int(a))
    elif o in "-d":
      user_input.append("-d %d" % int(a))
    elif o in "-t":
      user_input.append("-t %s" % str(a))
    elif o in "-b":
      user_input.append("-b %d" % int(a))
    else:
      logging.error("Error in input.  Option [-%s] not found" % o)
 
  f = open(file_name,'w')
  t = []
  for i in xrange(0,10):
    p = subprocess.Popen(['python3.3', 'dijkstra.py','-e','-p','-c','-x']+user_input,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.split('\n')
    nums = [k.split(':')[1] for k in out[:-1]]
    t.append(nums)

  
  setup = [float(k[0]) for k in t]
  alg = [float(k[1]) for k in t]
  netx = [float(k[2]) for k in t]

  f.write(str(user_input)+'\n')
  p_avg = reduce(lambda x, y: x + y, setup) / len(setup)
  q_avg = reduce(lambda x, y: x + y, alg) / len(alg)
  r_avg = reduce(lambda x, y: x + y, netx) / len(netx)
  p_var = map(lambda x: (x - p_avg)**2, setup)
  q_var = map(lambda x: (x - q_avg)**2, alg)
  r_var = map(lambda x: (x - r_avg)**2, netx)
  p_std = math.sqrt(average(p_var))
  q_std = math.sqrt(average(q_var))
  r_std = math.sqrt(average(r_var))

  f.write("%f, %f\n" % (p_avg,p_std))
  f.write("%f, %f\n" % (q_avg,q_std))
  f.write("%f, %f\n" % (r_avg,r_std))

  f.close()
