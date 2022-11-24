from z3 import *
import csv
from enum import Enum

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

pyboard = [[]]

# csv parsing
with open('robotplanning/demogrid.csv', 'r') as file:
    reader = csv.reader(file)
    pyboard = [list(map(int, i)) for i in list(reader)]
#pp(pyboard)

BOARD_SIZE = len(pyboard[0])

board = [[(Int("x_%s_y_%s" % (i,j))) for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)] 
pp(board)

board_c = []
for x in range(BOARD_SIZE):
    for y in range(BOARD_SIZE):
            board_c.append(board[x][y] == pyboard[x][y])
board_c = [And(board_c)]
#pp(board_c)
             
BEGIN = 0
END = 1
LAVA = 2
ICE = 3

start_positions = []
for x in range(0, BOARD_SIZE):
    for y in range(0, BOARD_SIZE):
        if pyboard[x][y] == 0:
            start_positions.append((x, y))
pp(start_positions)

# Configuration for colours and directions

maxValue = max(flatten(pyboard))

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
STAY = 4

# Define the tile direction list for all tiles
tileDirections = [Int("dir_%s" % (i)) for i in range(maxValue+1)]
# The direction for a tile is within the range of the direction enum
validDirection_c =[And(tileDirections[i] >= 0, tileDirections[i] <= 4) for i in range(maxValue+1) ]
#pp(validDirection_c)

# stay on the end if you reach it. (also stay on lava since we dont want the direction of lava to vary)
endPosition_c = [And(tileDirections[END] == STAY, tileDirections[LAVA] == STAY)]

# booleans for sliding
doesSlideList = [Bool("slide_%s" % (i)) for i in range(NO_STEPS)]

dontSlideOnStart_c = [doesSlideList[0] == False]

route = [(Int("x_%s" % (i)),Int("y_%s" % (i))) for i in range(NO_STEPS+1)]
pp(route)

#validMove_f = [And(board[route[step+1][0]][route[step+1][1]]) for step in range(NO_STEPS)]
print("TEST:")
pp(existsList([route[0]],route[0][0] == 3))
existRoute_f = [existsList(route, And(route[0][0] == startPos[0],route[0][1] == startPos[1], board[route[NO_STEPS][0]][route[NO_STEPS][1]] == END)) for startPos in start_positions] 
pp(existRoute_f)

validRoute_c = [ForAll(doesSlideList,existRoute_f)]
#pp(validRoute_c)

constraints = And(And(board_c), And(validDirection_c), And(endPosition_c) , And(dontSlideOnStart_c) , And(validRoute_c))

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
