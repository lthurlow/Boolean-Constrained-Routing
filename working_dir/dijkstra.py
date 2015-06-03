import networkx as nx
import os
import sys
import random
#import pycosat
import pyeda.inter
import time
import logging
import pdb
import heapq
import getopt

## Random number value and seed
prng = random.Random()
## Use symmetric boolean expression for links
symetric = False
## Use Policy Based Routing
pbr = 0
## for printing compare info
compare = 0
logging.basicConfig(level=logging.DEBUG)

class entry:
  def __init__(self, src, dest, cost, expr, pnt):
    self.src = src   ## added_by
    self.dest = dest ## this_node
    self.cost = cost ## cost
    self.expr = expr ## bool
    self.point = pnt # pointer to Ele obj (keep track)
  def __str__(self):
    string = "(%s,%s,%s,%s,{%s})" %\
    (self.src, self.dest, self.cost, self.expr, self.point)
    return string
  ## 2.7 compare method - implicit
  def __cmp__(self,other):
    return cmp(self.cost,other.cost)
  ## 3.0 compare method - explicit
  def __lt__(self,other):
    return (self.cost < other.cost)

class debug_turn:
  def __init__(self,cur_entry,visited,pre_pri_q,pred):
    self.current = cur_entry
    self.visited = visited
    self.pre_pri_q = pre_pri_q
    self.pred = pred
  def add_selected(self,selected):
    self.selected = selected
  def add_post_pri_q(self,pri_q):
    self.post_pri_q = pri_q
  def add_neighbors(self,neigh):
    self.curr_neighbors = neigh
  def __str__(self):
    string = '---'
    string += '\tCurrent Node: %s\n' % str(self.current)
    string += '\tNeighbors : %s\n' % self.curr_neighbors
    string += '\tPre Q: %s\n' % self.pre_pri_q
    string += '\tPost Q: %s\n' % self.post_pri_q
    string += '\tHeapify: %s\n' % heapsort(self.post_pri_q)
    string += '\tSelected: %s\n' % self.selected
    string += '\tPredecssor Queue Prior: %s\n' % self.pred
    return string

## Equivalent to sorted(iterable)
def heapsort(iterable):
    h = []
    for value in iterable:
      ## value is a tuple, and needs to specify first element to sort
      heapq.heappush(h, value[0])
    return [heapq.heappop(h) for i in range(len(h))]

## This function is used to check for the satisfiability of the clause
## Given a solution, if the clause does not evaluate as satisifiable,
## 'UNSAT' or 'UNKNOWN' are returned
def evaluate(clauses, sol):
  sol_vars = {}
  for i in sol:
    sol_vars[abs(i)] = bool(i>0)
  try:
    return all(any(sol_vars[abs(i)] ^ bool(i < 0) for i in clause)\
           for clause in clauses) 
  except KeyError:
    return bool(0)

## Determines the number of booleans that are used throughout
## the graph, this is used for a basis to expand all solutions
## to all variable solutions.
def return_vars(d):
  bvs = []
  for vert in d:
    for edge in d[vert]:
      props = d[vert][edge]
      bool_list = props[1][0]
      for bool_v in bool_list:
        if isinstance(bool_v,int):
          bvs.append(abs(bool_v))
        if isinstance(bool_v,list):
          for bv in bool_v:
            bvs.append(abs(bv))
  logging.debug('# variables detected: %s' % len(set(bvs)))
  return len(set(bvs))

## Main dijkstra function.
## Takes in a dictionary and a starting node
## pbr = 0 is normal dijkstra shortest path
## pbr = 1 is policy based dijkstra
## The function will return a dictionary of
## node, cost, path, and expression
def bool_dijkstra(graph,source):
  bool_vars = return_vars(graph) # How many booleans are used?
  temp_visit = graph.copy() ## Use for tracking non-visited nodes
  pri_q = [] ## List of nodes to select from
  ## dictionary of the dijkstra algorithm
  current = entry(source, source, 0, None, None) 
  predecessor = {source:[current]}
  ## keep track of the current node
  ## Assumed cost from A to A is 0, not predecessor
  ## Use selected to test the boolean expression for canadate
  selected = -1
  ## Use picked to decide if we have a legitimate canadate
  picked = True
  debug_dict = {}
  turn_counter = 0

  ## We should run this algorithm until we have explored both our
  ## original queue of nodes, as well as the updated neighbor list
  while ((not pbr and len(temp_visit) > 1) or 
             (pbr and (len(pri_q) or selected == -1))):
    this_turn = debug_turn(current,temp_visit,pri_q,predecessor)
    logging.debug( "-------------------" )
    logging.debug( '[%s]' % current )
    logging.debug( 'visited length: %s' % len(temp_visit) )
    logging.debug( 'cana length: %s' % len(pri_q) )
    logging.debug( 'PERM: %s' % predecessor)
    logging.debug( "-------------------" )

    ## If we picked a new vertex, we need to re-add all neighbors, and
    ## add the boolean expression and well as path cost of accepting this
    ## new node.  It is likely this node is not the shortest, so this will
    ## lead to a node being picked multiple times.
    if picked:
      ## For each of the neighbors to the vertex, add them back into the
      ## priority queue as legitate nodes for selection.
      for neighbors in graph[current.dest]:
        ## For all nodes that have already been chosen as predecessors,
        ## add their atributes to the current cost as well as boolean exprs.
        ### Check if the expression is Null
        if (current.expr):
          temp = entry(current.dest, neighbors,\
                graph[current.dest][neighbors][0]+current.cost,
                graph[current.dest][neighbors][1]+current.expr, current)
        else:
          temp = entry(current.dest, neighbors,\
                graph[current.dest][neighbors][0]+current.cost,
                graph[current.dest][neighbors][1], current)
        ## push onto priority queue
        heapq.heappush(pri_q, (temp.cost, temp))
      ## debug for neighbors
      this_turn.add_neighbors(graph[current.dest])
      this_turn.add_post_pri_q(pri_q)

      ## We now should have our legigate nodes for dijkstra to choose from
      ## with the updated neighbor list.
      available_costs = heapsort(pri_q) ## list of 

      logging.debug("\tInside Picked, after insert into heapqueue")
      logging.debug("\tList of costs: %s" % available_costs)

    ## Now set picked to false, and go through the selection process for the
    ## Next node.  When we choose that new node, we will set picked to True
    ## Then we will break out of this loop and fall back up top, add all of
    ## That node's neighbors w/ costs and boolean exprs.
    picked = False
    while not picked and len(pri_q) > 0:
      logging.debug( '\tcurrent: %s' % current )
      logging.debug( "\telements left in queue : %s" % len(pri_q) )
      logging.debug( "\tfirst cost in queue: %s" % available_costs[0])
      logging.debug( "\telements in queue: %s" % available_costs )

      ## Pop our potential canadate off the queue of legitimate choices
      selected = (heapq.heappop(pri_q))[1]
      added_by = selected.point
      this_turn.add_selected(selected)
      logging.debug( '\telement: %s' % str(selected))

      ## We only care about it if the object is not already in 
      if selected.dest not in predecessor:
        logging.debug( '\tadded-by: %s' % str(added_by))

        ## Special case due to modifying Dijkstra, is that we allow non-shortest paths
        ## to be added, becasue of this, non-shortest paths can be added before the
        ## shortest path, this leads to the case where the newly added non-shortest path
        ## Is not satisfiable.  This can even be the case for the shortest path.
        unsat = False
        if pbr:
          ## If the expression is not satisfiable, break out of here and skip to the
          ## next valid canadate, we will throw this one out
          ### python 3.0 replaced bastring type with str
          if selected.expr == [[]]:
            selected.expr = []
          pdb.set_trace()
          #XXX unsat = True if isinstance(pycosat.solve(selected.expr), str) else False
          ## can simply change list to DimacsCNF() - however all logic before using list must change.
          unsat = True if (selected.expr).satisfy_one() else False
          logging.debug('\tThe expresion: %s is %s' % (selected.expr, 'Sat' if not unsat else 'Unsat'))

        ## List should be empty as it has not been seen yet
        ## Update selected node and add it to predecessor dict
        if not unsat:
          predecessor[selected.dest] = [selected]
          picked = True
          debug_dict[turn_counter] = this_turn
          turn_counter+=1

      else:
        logging.debug("\tELSE")
        logging.debug("\t-------------------")
        if pbr: ## Check if we are doing policy based routing 
          current_bool = [selected.expr]
          prev_nodes = []
          pred_bools = []
          pred_name = []

          for nodes in predecessor[added_by.dest]:
            prev_nodes.append(nodes)

          ## We want all the boolean expressions of all nodes that have been
          ## Added already for this destination.
          for nodes in predecessor[selected.dest]:
            pred_bools.append(nodes)
            pred_name.append(nodes.dest)

          sol_set = [] ## Set of solution for this clause set
          ## Should only need to check the added_by field to stop 2 cycle loops
          ## Multiple cycle loops should be denied by evaluate, but 2 cycle loops
          ## that include source are un-evaluatable, as the source has no expr
          ## for which to evaluate on.
          logging.debug( "\t\tTrying to add: %s" % selected.dest )
          logging.debug( "\t\tWas added by: %s" % pred_name )
          logging.debug( "\t\tNow by: %s" % selected.src )
          for b in pred_bools:
            logging.debug( "\t\tOld Clause: %s" % b.expr )
          logging.debug( "\t\tNew Clause: %s" % selected.expr )

          for p in predecessor:
            for pp in predecessor[p]:
              logging.debug( "\t\tPred_DICT: (%s,%s) [%s] {%s}" %\
                ( p, pp.src, pp.cost, pp.expr) )

          ## Dont add our source back! No cycles through source.
          old_sol_set = []
          add_selected_node = False

          ##collect the solutions of all previously accepted solutions
          logging.debug('\tprevious clauses: %s' % pred_bools )
          for old_cases in pred_bools:
            temp_cases = old_cases
            if not temp_cases.expr:
              temp_cases.expr = []
            #XXX for solutions in pycosat.itersolve(temp_cases.expr,bool_vars):
            ### would need to expand to full list 
            for solutions in list((temp_cases.expr).satisfy_all()):
              old_sol_set.append(solutions)
  
          logging.debug('\t\tsolutions: %s' % old_sol_set)
          ## Test to see if current expression is even valid
          logging.debug('\t%s' % selected.expr )
          ### python 3.0 replaced bastring type with str
          #XXX unsat = True if isinstance(pycosat.solve(selected.expr,bool_vars),str)\
          #XXX        else False
          unsat = True if (selected.expr).satisfy_one() else False
          ## if this case in itself is satisfiable (e.g. not 2 and -2)
          if not unsat:
            ## Given our constaints on # of bools, find all solutions for this new_case
            #XXX for solutions in pycosat.itersolve(selected.expr,bool_vars):
            for solutions in list((selected.expr).satisfy_all()):
              if (solutions not in old_sol_set):
                add_selected_node = True

          ## We have atleast one solution which is not accounted for by other
          ## reviously accepted nodes, therefore, update the nodes cost and
          ## expression and accept node
          if add_selected_node:
            logging.debug('\t\t\tDid not find similar solution for this node.')
            picked = True
            predecessor[selected.dest].append(selected)
            debug_dict[turn_counter] = this_turn
            turn_counter+=1

            for p in predecessor:
              for pp in predecessor[p]:
                logging.debug("\t\tADDED_DICT: (%s,%s) [%s] (%s) {%s}" %\
                  ( p, pp.src, pp.cost, pp.point, pp.expr) )

        else:
          logging.debug( "\tupdated: %s" % pri_q )
          logging.debug( "\t-------------------\n")

      ## only update current if we selected a new node.
      #if (picked and selected in temp_visit):
      ## I think we want to re-add node to current list to re-propodate new bools
      if (picked):
        if current.dest in temp_visit:
          logging.debug("\tPopping: %s" % current.dest)
          temp_visit.pop(current.dest)
        logging.debug( "\tStill Un-explored: %s" % temp_visit.keys() )
        current = selected
  return (predecessor,debug_dict)

## Random Boolean Expression Generator
def genex(variables, rand_type):
  if isinstance(variables, int):
    ## Simpleton approach using 1 variable with range [-#,#]
    if rand_type == 'pyrand':
      logging.debug('pyrand- genex function')
      x = prng.randint(0,1)
      if x:
        return [[prng.randint(-1*variables,-1)]]
      else:
        return [[prng.randint(1,variables)]]
    ## More elegant: Use pyeda to generate truthtable
    ## Convert truth table back to readable solution for pyco
    elif rand_type == 'pyeda':
      expr = []
      logging.debug('pyeda- genex function')
      gen_truth = lambda n: [prng.randint(0,1) for b in range(1,n+1)]
      X = pyeda.inter.bitvec('x',variables)
      TT = pyeda.inter.truthtable(X,gen_truth(2**variables))
      EX = pyeda.inter.truthtable2expr(TT)
      logging.debug('EXPR = %s' % EX)
      logging.debug('TT = %s' % TT)
      try:
        logging.debug("Before e2d")
        CNF = pyeda.inter.expr2dimacscnf(EX.to_cnf(flatten=False))
        logging.debug("After e2d")
        CNF_STR = CNF.__str__().split('\n')[1:]
        logging.debug('DIMACNF STR FORMAT: %s' % CNF_STR)
        for clause in CNF_STR:
          sub_clause = []
          line = clause.split(' ')[:-1]
          for ele in line:
            sub_clause.append(int(ele))
          expr.append(sub_clause)
        logging.debug('As a list: %s' % expr)
      except ValueError:
        logging.info('Have to recall genex, solution not satisfiable')
        expr = genex(variables, rand_type)
      return expr
      
    else:
      logging.error('Invalid style given!')
      logging.info('Invalid style given!')
      exit(1)
  else:
    logging.error('variable non-integer')
    logging.info('variable non-integer')
    exit(1)
    
## Adds boolean expressions to each link with a list as input
## returns a dictionary with dest as key, and src, dist, expr as value
def add_boolean(v_list, variables, rand_type):
  d1 = {}
  if (not symetric):
    v_list = nx.DiGraph(v_list)
  for t in sorted(v_list.edges()):
    edge_weight1 = prng.randint(0,10)
    edge_bool1 = genex(variables, rand_type)
    if (symetric):
      v_list.add_edge(t[0],t[1],weight=edge_weight1)
      if t[0] in d1:
        d1[t[0]] = dict(sorted(d1[t[0]].items())+
                   list({t[1]:(edge_weight1,edge_bool1)}.items()))
      else:
        d1[t[0]] = {t[1]:(edge_weight1,edge_bool1)}
      if t[1] in d1:
        d1[t[1]] = dict(sorted(d1[t[1]].items())+
                   list({t[0]:(edge_weight1,edge_bool1)}.items()))
      else:
        d1[t[1]] = {t[0]:(edge_weight1,edge_bool1)}
    else:
      edge_weight2 = prng.randint(0,10)
      edge_bool2 = genex(variables, rand_type)
      v_list.add_edge(t[0],t[1],weight=edge_weight1)
      #v_list.add_edge(t[0],t[1],weight=edge_weight2)
      if t[0] in d1:
        d1[t[0]] = dict(sorted(d1[t[0]].items())+
                   list({t[1]:(edge_weight1,edge_bool1)}.items()))
      else:
        d1[t[0]] = {t[1]:(edge_weight1,edge_bool1)}
      if t[1] in d1:
        d1[t[1]] = dict(sorted(d1[t[1]].items())+
                   list({t[0]:(edge_weight2,edge_bool2)}.items()))
      else:
        d1[t[1]] = {t[0]:(edge_weight2,edge_bool2)}
  return (d1,v_list)

def organize_graph(d1):
  dx = {} ## holds ints rather than strings
  for k in sorted(d1):
    p = dict((int(k),(int(v[0]),v[1])) for k,v in d1[k].items())
    dx[int(k)] = p
  return dx

def main(user_input):
  ## Use networkx to generate graph
  time_now = time.time()
  G = nx.random_regular_graph(user_input['d'],user_input['n'],seed=user_input['s'])
  ## Update list with boolean expressions for each link
  (update_graph,G) = add_boolean(G, user_input['b'], user_input['t'])
  ## Resort the dictionary to be of integer types rather than strings.
  adj_matrix = organize_graph(update_graph)
  time_stop = time.time()
  setup_time = time_stop - time_now

  logging.info('') 
  time_now = time.time()
  ## python3.3 convert adj_matrix.keys() to list from dict_keys
  ## Added it to be a tuple, so debug is the second element returned
  (shortest_sat,debug_info) = bool_dijkstra(adj_matrix, list(adj_matrix.keys())[0])
  time_stop = time.time()
  logging.info("")
  logging.info("")
  logging.info(adj_matrix)
  logging.info("")
  logging.info("")

  print("Setup Time is: %s" % (setup_time) )
  print("Alg Run time: %s" % (time_stop-time_now) )
  logging.info("")
  logging.info("")
  for v in adj_matrix.keys():
    try:
      dist = shortest_sat[v]
      count = 0
      for vt in dist:
        if count == 0:
          logging.info("source:%s, dest: %s, DIST: %s, PATH: %s, EXPR: %s" %\
                 (list(adj_matrix.keys())[0], v, vt.cost,vt.point, vt.expr))
        else:
          logging.info("\t\t     DIST: %s, PATH: %s, EXPR: %s" % (vt.cost,vt.point, vt.expr))
        count += 1
    except KeyError:
      logging.info("source:%s, dest: %s, NO VALID PATH" %\
           (list(adj_matrix.keys())[0], v))

  time_now = time.time()
  netx = nx.single_source_dijkstra_path(G, G.nodes()[0])
  time_stop = time.time()
  netx_dist = {}
  if compare:        
    logging.info("")
    print("Netx Run time: %s" % (time_stop-time_now) )
    logging.info("")
    logging.info(netx)
    logging.info("")
  
  if symetric:
    for v in adj_matrix.keys():
      dist = nx.dijkstra_path_length(G, v,list(adj_matrix.keys())[0])
      netx_dist[v] = dist
      if compare:
        logging.info("source:%s, dest: %s, DIST: %s" %\
             (list(adj_matrix.keys())[0], v, dist))
  else:
    for v in adj_matrix.keys():
      dist = nx.bidirectional_dijkstra(G,v,list(adj_matrix.keys())[0])
      netx_dist[v] = dist[1][0]
      if compare:
        logging.info("source:%s, dest: %s, DIST: %s" %\
             (list(adj_matrix.keys())[0], v, dist))

  logging.debug('')
  logging.debug('')
  ## Compare distance lists from both
  logging.debug('Difference List')
  for k in adj_matrix.keys():
    try:
      if (shortest_sat[k][0].cost < netx_dist[k]):
        logging.error( "-------------------" )
        logging.error('ERROR: Vertex %s is not the same' % k)
        logging.error("NETX source:%s, dest: %s, DIST: %s" %\
             (list(adj_matrix.keys())[0], k, netx_dist[k]))
        logging.error("MINE source:%s, dest: %s, DIST: %s" %\
             (list(adj_matrix.keys())[0], k, shortest_sat[k][0].cost))
        logging.error( "-------------------" )
    except KeyError:
      logging.debug('No valid path for vertex %s' % k)
  

def print_args():
  print("Policy Based Routing using Dijkstra Shortest Path:")
  print("h:\tprints this menu.")
  print("v:\tprints logging information.")
  print("n:\t-n [10] graph uses 10 vertices/nodes.")
  print("d:\t-d [4] each vertice on averages has 3 neighbors.")
  print("s:\t-s [100] seeds the random number generator.")
  print("t:\t-t ['pyeda'] uses pyeda module to select boolean expressions.")
  print("b:\t-b [4] indicates 4 boolean variables will be used.")
  print("f:\t-f ['output.txt'] saves output to a file.")
  print("c:\tcompares against networkx dijkstra run time.")
  print("e:\tsets the graph to have bi-directional links with equal values.")
  print("p:\tturns on policy based routing protol, defaults to dijkstra")
  print("")

## Call main function.
if __name__ == "__main__":
  user_input = {}
  nodes = 10
  degree = 4 ## takes the floor for int
  seed = 100
  write_file = False
  bool_rand = 'pyeda'
  num_bools = 4
  verbose = False
  nothing = False
  opts = args = ''
  try:
    opts, args = getopt.getopt(sys.argv[1:], "n:d:s:t:b:f:pvhecx", ["help","file"])
  except getopt.GetoptError:
    print_args()
    sys.exit(1)
  for o, a in opts:
    #logging.debug('option: %s, argument: %s' % (o,a))
    if o == "-v":
      verbose = True
    elif o in ("-h", "--help"):
      print_args()
      exit(0)
    elif o in ("-f","--file"):
      write_file = str(a)
    elif o in "-n":
      nodes = int(a)
    elif o in "-d":
      degree = int(a)
    elif o in "-s":
      seed = int(a)
    elif o in "-p":
      pbr = 1
    elif o in "-e":
      symetric = True
    elif o in "-t":
      bool_rand = str(a)
    elif o in "-b":
      num_bools = int(a)
    elif o in "-c":
      compare = True
    elif o in "-x":
      nothing = True
    else:
      logging.error("Error in input.  Option [-%s] not found" % o)
  
  ## Set user_input dict for input into program
  user_input['n'] = nodes
  user_input['d'] = degree
  user_input['t'] = bool_rand
  user_input['b'] = num_bools
  user_input['s'] = seed

  if verbose and write_file:
    logging.basicConfig(filename=write_file,filemode='a',\
                        level=logging.DEBUG)
  elif verbose:
    logging.basicConfig(level=logging.DEBUG)
  elif nothing:
    logging.disable(logging.DEBUG)
    logging.disable(logging.INFO)
  else:
    logging.disable(logging.DEBUG)
    #logging.basicConfig(level=logging.INFO)
  prng.seed(seed)
  main(user_input)
