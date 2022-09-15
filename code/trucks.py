from z3 import *
NO_TRUCKS = 8 # Number of trucks
CAPACITY = 8 # Truck size in number of pallets
MAX_WEIGHT = 8000 #maximum truck weight in kg
NO_ITEM_TYPES = 5 # The number of different pallets
# Define trucks,
# a 2 dimentional list with the trucks and the different item types
trucks = [ [ Int("x_%s_%s" % (i, j+1)) for j in range(NO_ITEM_TYPES) ]
      for i in range(NO_TRUCKS) ]

# Define the lookup table to the weight of the items
#4 Nuzzles, Prittles, 8 Skipples, 10 Crottles, 20 Dupples
NUZZLES_INDEX = 0
PRITTLES_INDEX = 1
SKIPPLES_INDEX = 2
CROTTLES_INDEX = 3
DUPPELES_INDEX = 4

ITEM_WEIGHTS = (700,400,1000,2500,200)
ITEM_NMUMBERS = (4, 0, 8, 10, 20)
# No negative amounts
nonnegative_c = [ And ( [ trucks[i][j] >= 0 for j in range(NO_ITEM_TYPES) ] )
      for i in range(NO_TRUCKS) ]
# We need to fit at least all of the numbered items into the trucks
items_c = [ And( [ sum ([ trucks[i][j] for i in range(NO_TRUCKS) ]) >= ITEM_NMUMBERS[j] ] ) for j in range(NO_ITEM_TYPES) ]
requirements_c = nonnegative_c +  items_c

# Weight is constrained to 8000kg per truck
weights = [ [ ITEM_WEIGHTS[j] * trucks[i][j] for j in range(NO_ITEM_TYPES) ]
        for i in range(NO_TRUCKS) ]
weights_c = [ sum(weights[i]) <= MAX_WEIGHT  for i in range(NO_TRUCKS) ]
# Capacity is constrained to 8 pallets per truck
capacities_c = [ sum(trucks[i]) <= CAPACITY for i in range(NO_TRUCKS) ]

# Skipples need to be cooled; only three of the eight trucks have facility for cooling skipples.
cooled_trucks = 3
cooled_c = [ trucks[i][2] == 0 for i in range(cooled_trucks, NO_TRUCKS) ]

#Nuzzles are very valuable: to distribute the risk of loss no two pallets of nuzzles may be in the same truck
valuable_nuzzles_c = [ trucks[i][NUZZLES_INDEX] < 2 for i in range(NO_TRUCKS) ]

#Prittles and crottles are an explosive combination: they are not allowed to be put in the same truck.
# e.g. gor each truch not (more than zero Prittles and more than zero Crottles)
prittles_crottles_c = [ Not(And(trucks[i][PRITTLES_INDEX] > 0, trucks[i][CROTTLES_INDEX] > 0 )) for i in range(NO_TRUCKS) ]

# Maximize the number of prittles
opt = Optimize()
# 1.
#opt.add(requirements_c + weights_c + capacities_c + cooled_c + valuable_nuzzles_c)
# 2.
opt.add(requirements_c + weights_c + capacities_c + cooled_c + valuable_nuzzles_c + prittles_crottles_c)
opt.maximize( sum([ trucks[i][PRITTLES_INDEX] for i in range(NO_TRUCKS) ]))
opt.set('priority', 'box')
res = opt.check()
print(res)
m = opt.model()
max_prittles = sum ( [ m.evaluate(trucks[i][PRITTLES_INDEX]) for i in range(NO_TRUCKS) ] )
print(max_prittles)
print(simplify(max_prittles))
r = [ [ m.evaluate(trucks[i][j]) for j in range(NO_ITEM_TYPES) ]
          for i in range(NO_TRUCKS) ]
print_matrix(r)
# Solve the problem and print the model
#s = Solver()
#s.add(requirements_c + weights_c + capacities_c)
#res = s.check()
#print(res)
#print(s.model())