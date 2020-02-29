import math
import itertools
import time
from pydstarlite import dstarlite, utility


start_time = time.time()
robots = ['a1', 'a2', 'a3', 'a4','a5']
goals = ['b1', 'b2', 'b3','b4','b5']

prob =  [list(zip(each_permutation, goals)) for each_permutation in itertools.permutations(robots, len(goals))]

elapsed_time = time.time() - start_time
print(elapsed_time)
