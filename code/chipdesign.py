from z3 import *
from colorama import Fore, Back, Style

# used for summing boolean


def boolListToInt(l):
    return If(l, 1, 0)


def sumBool(l):
    return sum(map(boolListToInt, l))


def get_colour(index):
    match index:
        case 0:
            return Back.BLACK
        case 1:
            return Back.YELLOW
        case 2:
            return Back.YELLOW
        case 3:
            return Back.CYAN
        case 4:
            return Back.GREEN
        case 5:
            return Back.LIGHTBLUE_EX
        case 6:
            return Back.LIGHTMAGENTA_EX
        case 7:
            return Back.MAGENTA
        case 8:
            return Back.RED
        case 9:
            return Back.LIGHTRED_EX
        case 10:
            return Back.LIGHTBLACK_EX
        case 11:
            return Back.LIGHTGREEN_EX
        case 12:
            return Back.LIGHTWHITE_EX
        case default:
            return Back.WHITE


def printlist(l):
    board = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]
    chipNumber = 1
    for chip in l:
        for x in range(chip[0], chip[0] + chip[2]):
            for y in range(chip[1], chip[1] + chip[3]):
                if (x >= 0 and x <= WIDTH and y >= 0 and y <= HEIGHT):
                    board[y][x] = chipNumber
        chipNumber += 1
    for x in range(HEIGHT):
        row = ""
        for y in range(WIDTH):
            row += get_colour(board[x][y])
            row += "{:2d} ".format(board[x][y])
        print(row + Back.RESET)


# Width of the chip
WIDTH = 30
HEIGHT = 30
# Distance between center of components because of heat
HEAT_DIST = 18

# list of components, first element is width, second is height
components = [(4, 3), (4, 3), (4, 5), (4, 6), (5, 20), (6, 9),
             (6, 10), (6, 11), (7, 8), (7, 12), (10, 10), (10, 20)]
#components = [(15, 29), (15, 29), (1, 2), (1, 2)]
# first 2 components are power components

NO_POWER_COMPONENTS = 2
power_components = components[0:NO_POWER_COMPONENTS]
NO_COMPONENTS = len(components)


def rotate(c):
    return (c[1], c[0])

def distance_squared(p1,p2):
    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

def get_center(comp):
    return (comp[COMP_X]+comp[COMP_WIDTH]/2,comp[COMP_Y]+comp[COMP_HEIGHT]/2)

def center(c):
    return (c[0]/2, c[1]/2)
    #return (math.ceil((c[0]/2) - 1) , math.ceil((c[1]/2) - 1))

# list with elements {topleft x, topleft y, width, height}
# x increase to right, y increase to bottom
#chip = [[0,0,3,4], [4,4,1,5], [6,7,8,8]]
COMP_X = 0
COMP_Y = 1
COMP_WIDTH = 2
COMP_HEIGHT = 3
COMP_ATTRIBUTES = 4


def getname(attr):
    match attr:
        case 0:
            return "x"
        case 1:
            return "y"
        case 2:
            return "width"
        case default:
            return "height"


# Define chip datastructure
chip = [[Int("Comp%s_%s" % (comp, getname(x))) for x in range(COMP_ATTRIBUTES)]
        for comp in range(NO_COMPONENTS)]

# define the constraints

# x and y at least 0 and not bigger than width and height (minus 1)
in_bounds_c = [And(chip[comp][COMP_X] >= 0, chip[comp][COMP_Y] >= 0, chip[comp][COMP_X] + chip[comp][COMP_WIDTH]
                   <= WIDTH, chip[comp][COMP_Y] + chip[comp][COMP_HEIGHT] <= HEIGHT) for comp in range(NO_COMPONENTS)]

# chip of right size
correct_size_c = [Or(And(chip[comp][COMP_WIDTH] == components[comp][0], chip[comp][COMP_HEIGHT] == components[comp][1]),
                     And(chip[comp][COMP_WIDTH] == components[comp][1], chip[comp][COMP_HEIGHT] == components[comp][0])) for comp in range(NO_COMPONENTS)]

# chips cannot overlap, take 2 different components and ensure they do not overlap, do this for all components
overlap_c = []
for c1 in range(NO_COMPONENTS):
    for c2 in range(NO_COMPONENTS):
        if (c1 < c2):
            overlap_c.append(Or(chip[c2][COMP_X] >= chip[c1][COMP_X] + chip[c1][COMP_WIDTH], chip[c2][COMP_Y] >= chip[c1][COMP_Y] + chip[c1][COMP_HEIGHT],
                             chip[c2][COMP_X] + chip[c2][COMP_WIDTH] <= chip[c1][COMP_X], chip[c2][COMP_Y] + chip[c2][COMP_HEIGHT] <= chip[c1][COMP_Y]))

# In order to get power, all regular components should directly be connected to a power component, that is, an edge of the component should have a part of length > 0 in common with an edge of the power component.
power_c = []
for c in range(NO_POWER_COMPONENTS, NO_COMPONENTS):
    for pc in range(NO_POWER_COMPONENTS):
            # Top and Bottom
            above_or_below = Or([(And(chip[c][COMP_X] < chip[pc][COMP_X] + chip[pc][COMP_WIDTH], chip[c][COMP_X] + chip[c][COMP_WIDTH] > chip[pc][COMP_X], Or(chip[c][COMP_Y] + chip[c][COMP_HEIGHT] == chip[pc][COMP_Y], chip[c][COMP_Y] == chip[pc][COMP_Y] + chip[pc][COMP_HEIGHT]))) for pc in range(NO_POWER_COMPONENTS)])
            # Left or Right
            left_or_right  = Or([(And(chip[c][COMP_Y] < chip[pc][COMP_Y] + chip[pc][COMP_HEIGHT], chip[c][COMP_Y] + chip[c][COMP_HEIGHT] > chip[pc][COMP_Y], Or(chip[c][COMP_X] + chip[c][COMP_WIDTH] == chip[pc][COMP_X], chip[c][COMP_X] == chip[pc][COMP_X] + chip[pc][COMP_WIDTH]))) for pc in range(NO_POWER_COMPONENTS)])
            
            power_c.append(Or(above_or_below, left_or_right))

def abs(x):
    return If(x >= 0,x,-x)

# Due to limits on heat production the power components should be not too close: their centres should differ at least 16 in either the x direction or the y direction (or both).
# heat_c = [ Or (abs((chip[0][COMP_X] + center(components[0])[0] - 1) - (chip[1][COMP_X] + center(components[1])[0] - 1)) >= HEAT_DIST , (abs((chip[0][COMP_Y] + center(components[0])[1] - 1) - (chip[1][COMP_Y] + center(components[1])[1]) - 1 ) >= HEAT_DIST)) ]
heat_c = []
for pc1 in range(NO_POWER_COMPONENTS):
    for pc2 in range(NO_POWER_COMPONENTS):
        if (pc1 < pc2):
            #for all pairs of power components, make sure the distance is bigger or equal to the heat distance (we square the HEAT_DIST instead of a square root in the )
            heat_c.append(Or(abs(chip[pc1][COMP_X] - chip[pc2][COMP_X]) >= HEAT_DIST, abs(chip[pc1][COMP_Y] - chip[pc2][COMP_Y]) >= HEAT_DIST))

basic_c = in_bounds_c + correct_size_c + overlap_c + power_c + heat_c

# Solve the problem and print the model
s = Solver()
s.add(basic_c)
res = s.check()
pp(res)

if res == sat:
    m = s.model()
    chipmodel = [[m.evaluate(chip[comp][x]).as_long() for x in range(
        COMP_ATTRIBUTES)] for comp in range(NO_COMPONENTS)]
    pp(chipmodel)
    printlist(chipmodel)
else:
    pass
