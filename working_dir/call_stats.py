import os, sys
import subprocess
import getopt
import pdb
import math

def print_args():
  print("CALL using Dijkstra Shortest Path:")
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
  key_trans = {"node":"-n","deg":"-d","bool":"-b"}
  user_input = []
  min_node = 0
  max_node = 0
  min_deg = 0
  max_deg = 0
  min_bool = 0
  max_bool = 0
  skip = 1
  file_name = "info.txt"
  try:
    opts, args = getopt.getopt(sys.argv[1:], "n:N:d:D:b:B:f:s:t:h", ["help","file"])
  except getopt.GetoptError:
    print_args()
    sys.exit(1)
  for o, a in opts:
    #logging.debug('option: %s, argument: %s' % (o,a))
    if o in ("-h", "--help"):
      print_args()
      exit(0)
    elif o in ("-f","--file"):
      file_name = str(a)
    elif o in "-n":
      min_node = int(a)
    elif o in "-N":
      max_node = int(a)
    elif o in "-d":
      min_deg = int(a)
    elif o in "-D":
      max_deg = int(a)
    elif o in "-t":
      user_input.append("-t %s" % str(a))
    elif o in "-b":
      min_bool = int(a)
    elif o in "-B":
      max_bool = int(a)
    elif o in "-s":
      skip = int(a)
    else:
      logging.error("Error in input.  Option [-%s] not found" % o)

  selected = {}
  if max_node - min_node != 0:
    selected['node'] = range(min_node,max_node+1,skip)
  if max_deg - min_deg != 0:
    selected['deg'] = range(min_deg,max_deg+1,skip)
  if max_bool - min_bool != 0:
    selected['bool'] = range(min_bool,max_bool+1,skip)
  if len(selected.keys()) == 0:
    print("Error no options selected!")
    exit(1)

  options = selected.keys()
  len_opt = len(options)

  res = open(file_name,'w')
  res.close()
  res = open(file_name,'a')

  cmd = ['python', 'stats.py']
  for y in selected[options[0]]:
    if (len_opt > 1):
      for x in selected[options[1]]:
        if (len_opt > 2):
          for z in selected[options[2]]:
            """
            print cmd+[key_trans[options[0]]]+[str(y)]+\
            [key_trans[options[1]]]+[str(x)]+\
            [key_trans[options[2]]]+[str(z)]
            """
            p = subprocess.Popen(cmd+[key_trans[options[0]]]+[str(y)]+\
                                 [key_trans[options[1]]]+[str(x)]+
                                 [key_trans[options[2]]]+[str(z)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            fd = open('default.txt','r')
            for line in fd:
              res.write(line)
            fd.close()
            
        else:
          """
          print cmd+[key_trans[options[0]]]+[str(y)]+\
               [key_trans[options[1]]]+[str(x)]
          """
          p = subprocess.Popen(cmd+[key_trans[options[0]]]+[str(y)]+\
                               [key_trans[options[1]]]+[str(x)],
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          out, err = p.communicate()
          fd = open('default.txt','r')
          for line in fd:
            res.write(line)
          fd.close()

    else:
      #print cmd+str(key_trans[options[0]])+str(y)
      p = subprocess.Popen(cmd+[key_trans[options[0]]]+[str(y)],
              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      out, err = p.communicate()
      fd = open('default.txt','r')
      for line in fd:
        res.write(line)
      fd.close()
          
