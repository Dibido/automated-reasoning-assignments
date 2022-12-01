from z3 import *
import csv
from enum import Enum

tileDirections = [Int("dir_%s" % (i)) for i in range(6)]

# flatten a 2d array (used to get max value)
def flatten(seq):
    for el in seq:
        if isinstance(el, list):
            yield from flatten(el)
        else:
            yield el     

def existsList(list,cond):
    if len(list) == 0:
        return cond
    else:
        return existsList(list[1:],Exists(list[0],cond))

NO_STEPS = 11




# board = [[(Int("board:x_%s_y_%s" % (i,j))) for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)] 
# #pp(board)

# board_c = []
# for x in range(BOARD_SIZE):
#     for y in range(BOARD_SIZE):
#             board_c.append(board[x][y] == pyboard[x][y])
# board_c = [And(board_c)]
#pp(board_c)
             
BEGIN = 0
END = 1
LAVA = 2
ICE = 3



LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
STAY = 4


list = [2,2,3,1]
# Define the tile direction list for all tiles
myvar = Int("myvar")
# The direction for a tile is within the range of the direction range

listInv = [[],[3],[0,1],[2]]

def getIndex(list,x,target):
    Or([Or([And(list[i][j] == target, x == i) for j in range(len(list[i]))])for i in range(len(list))])

def plus(a,b):
    return len(a)+b+3


validRoute_c = getIndex(listInv,myvar,3)
#pp(validRoute_c)

constraints = And( validRoute_c)
#constraints = And(And(board_c), And(validDirection_c), And(endPosition_c) , And(dontSlideOnStart_c) , And(validRoute_c))

s = Solver()
s.add(constraints)
res = s.check()
print(res)
if res == sat:
    print(s.model())
else:
    pass

'''
for N steps

given a configuration that maps "colours" to directions. 

for all booleans "slide" defining if it will slide on ice or not on every step
        list of size N

for every start position:
    ther eixists a route that ends in an end position

where a route sarts in a start position and every next position is reachable from the previous step determided by the configuration and the booleans
        list of size N + 1 (one for initial state)

'''
