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

NO_STEPS = 1

pyboard = [[]]

# csv parsing
with open('robotplanning/test.csv', 'r') as file:
    reader = csv.reader(file)
    pyboard = [list(map(int, i)) for i in list(reader)]
#pp(pyboard)
maxValue = max(flatten(pyboard))
BOARD_SIZE = len(pyboard[0])

pycoords = [[]]

for x in range(maxValue):
    pycoords.append([])

for x in range(BOARD_SIZE):
    for y in range(BOARD_SIZE):
        pycoords[pyboard[x][y]].append((x,y))

#pp(pycoords)

BEGIN = 0
END = 1
LAVA = 2
ICE = 3

board = z3.Array('board', z3.IntSort(), z3.IntSort())
for i in range(len(pyboard)):
    for j in range(BOARD_SIZE):
        board = Store(board, i+j*BOARD_SIZE,pyboard[i][j])
board = Store(board, -1,LAVA)
#pp(board)
#pp(pyboard)

# board = [[(Int("board:x_%s_y_%s" % (i,j))) for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)] 
# #pp(board)

# board_c = []
# for x in range(BOARD_SIZE):
#     for y in range(BOARD_SIZE):
#             board_c.append(board[x][y] == pyboard[x][y])
# board_c = [And(board_c)]
#pp(board_c)


start_positions = []
for x in range(0, BOARD_SIZE):
    for y in range(0, BOARD_SIZE):
        if pyboard[x][y] == 0:
            start_positions.append((x, y))
#pp(start_positions)

# Configuration for colours and directions
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
STAY = 4

# Define the tile direction list for all tiles
# tileDirections = [Int("dir_%s" % (i)) for i in range(maxValue+1)]
# TODO change into Z3 array
tileDirections = z3.Array('tiledirections', z3.IntSort(), z3.IntSort())

# The direction for a tile is within the range of the direction range
validDirection_c =[And(tileDirections[i] >= 0, tileDirections[i] <= 4) for i in range(maxValue+1) ]
#pp("directions")
#pp(validDirection_c)

# stay on the end if you reach it. (also stay on lava since we dont want the direction of lava to vary)
endPosition_c = [And(tileDirections[END] == STAY, tileDirections[LAVA] == STAY)]

# booleans for sliding
doesSlideList = [Bool("slide_%s" % (i)) for i in range(NO_STEPS)]

dontSlideOnStart_c = [doesSlideList[0] == False]

# route in the format xory +index*2 (where x =0 and y =1 for xory)
# e.g. to get the y at step 3 you would use route[1+3*2]
route = [Int("route_%s" % (i)) for i in range((NO_STEPS+1)*2)]

# check that every route index is within the board
validRouteIndex_c = [And(route[i] > 0,route[i] < BOARD_SIZE) for i in range((NO_STEPS+1)*2)]

#print("TEST:")

#validMove_f = [If(board[route[0+step*2]+route[1+step*2]*BOARD_SIZE] == ICE,If(doesSlideList[step],And(),And()),And()) for step in range(NO_STEPS)]
#pp(existsList([route[0]],route[0][0] == 3))

# TODO Helper function
def next3453Move(currentTileDirection, slide):
    if currentTileDirection == LEFT:
        if not slide:
            return (-1, 0)
        else:
            return (-2, 0)
    elif currentTileDirection == RIGHT:
        if not slide:
            return (1, 0)
        else:
            return (2, 0)
    elif currentTileDirection == UP:
        if not slide:
            return (0, -1)
        else:
            return (0, -2)
    elif currentTileDirection == DOWN:
        if not slide:
            return (0, 1)
        else:
            return (0, 2)
    elif currentTileDirection == STAY:
        return (0,0)
    else:
        return "error"


# TODO Helper function
def nextMove(tilePositionX ,tilePositionY ,currentTileDirection):
   return If(And(currentTileDirection == LEFT, tilePositionX - 1 >= 0),tilePositionX - 1 + tilePositionY*BOARD_SIZE ,
            If(And(currentTileDirection == RIGHT, tilePositionX + 1 < BOARD_SIZE),tilePositionX + 1 + tilePositionY*BOARD_SIZE , 
            If(And(currentTileDirection == UP, tilePositionY - 1 >= 0),tilePositionX  + (tilePositionY- 1)*BOARD_SIZE , 
            If(And(currentTileDirection == DOWN, tilePositionY + 1 < BOARD_SIZE),tilePositionX  + (tilePositionY+ 1)*BOARD_SIZE , 
            If(currentTileDirection == STAY,tilePositionX  + tilePositionY*BOARD_SIZE , -1 )))))

def move2(tilePositionX ,tilePositionY ,currentTileDirection):
   return If(And(currentTileDirection == LEFT, tilePositionX - 2 >= 0),tilePositionX - 2 + tilePositionY*BOARD_SIZE ,
            If(And(currentTileDirection == RIGHT, tilePositionX + 2 < BOARD_SIZE),tilePositionX + 2 + tilePositionY*BOARD_SIZE , 
            If(And(currentTileDirection == UP, tilePositionY - 2 >= 0),tilePositionX  + (tilePositionY- 2)*BOARD_SIZE , 
            If(And(currentTileDirection == DOWN, tilePositionY + 2 < BOARD_SIZE),tilePositionX  + (tilePositionY+ 2)*BOARD_SIZE , -1))))


pp(route)
# TODO current idea:
# Current tile direction is LEFT, if we do not slide, new tile is LEFT aka X-1 , if we do it is LEFT LEFT aka X-2, 
# else the previous tiledirection is not LEFT and we have to check the other options
# How to set step+1? using == ?
#validNextMoveLeft_f = [If(tileDirections[board[route[0+step*2]+route[1+step*2]*BOARD_SIZE]] == LEFT, If(not doesSlideList[step], And(route[0+step+1*2] == route[0+step*2] - 1, route[1+step+1*2] == route[1+step*2]) ,And(route[0+step+1*2] == route[0+step*2] - 2, route[1+step+1*2] == route[1+step*2])), And()) for step in range(NO_STEPS) ]
# ^ try to generalise this for all directions and ice conditions?
#validMove_f = [ [ If(tileDirections[board[route[0+step*2]+route[1+step*2]*BOARD_SIZE]] == direction, If(doesSlideList[step], And(route[0+step+1*2] == route[0+step*2]+nextMove(direction, True)[0] , route[1+step*2]+nextMove(direction, True)[1]), And(route[0+step+1*2] == route[0+step*2]+nextMove(direction, False)[0] , route[1+step*2]+nextMove(direction, False)[1])), And()) for direction in tileDirections ] for step in range(NO_STEPS) ] 
validMove_f = And([And(If(And(doesSlideList[step],board[nextMove(route[0+step*2],route[1+step*2],tileDirections[board[route[0+step*2]+route[1+step*2]*BOARD_SIZE]])]==ICE),move2(route[0+step*2],route[1+step*2],tileDirections[board[route[0+step*2]+route[1+step*2]*BOARD_SIZE]]) == route[0+(step+1)*2]+route[1+(step+1)*2]*BOARD_SIZE, nextMove(route[0+step*2],route[1+step*2],tileDirections[board[route[0+step*2]+route[1+step*2]*BOARD_SIZE]]) == route[0+(step+1)*2]+route[1+(step+1)*2]*BOARD_SIZE )) for step in range(NO_STEPS) ])# ^ this checks whether for every step, every direction we slide and makes the according move using a lookup function
# ^ how to deal with the empty And() at the end when it is not the  currently checked direction?
# ^ also 4 lookups into nextMove needed

# not slide | do silde AND ice in direction
pp(start_positions)
pp(board)
# There exists a route, starting on 
existRoute_f = [Exists(route, And(validMove_f,route[0+0*2] == startPos[0],route[1+0*2] == startPos[1], Select(board,route[0+NO_STEPS*2]+route[1+NO_STEPS*2]*BOARD_SIZE) == END )) for startPos in start_positions] 
#pp(existRoute_f)

validRoute_c = [ForAll(doesSlideList,existRoute_f)]
#pp(validRoute_c)

constraints = And(And(validDirection_c), And(endPosition_c) , And(dontSlideOnStart_c) , And(validRouteIndex_c), And(existRoute_f))
#constraints = And(And(board_c), And(validDirection_c), And(endPosition_c) , And(dontSlideOnStart_c) , And(validRoute_c))

s = Solver()
s.add(constraints)
res = s.check()
print(res)
if res == sat:
    pp(s.model())

    # f = open("model.out", "w")
    # for row in s.model():
    #     print(", ".join(row), file=f)
    # f.close()
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
