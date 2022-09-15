from z3 import *

NO_ROUNDS = 5
NO_HOUSES = 5
NO_PEOPLE = 10

dinner_schedule = [[[Int("R%s_H%s_P%s" % (r, h, p)) #could not use bool since sum does not take bools.
                     for p in range(NO_PEOPLE)]
                    for h in range(NO_HOUSES)]
                   for r in range(NO_ROUNDS)]

person_to_house_index = [p//(NO_PEOPLE//NO_HOUSES) for p in range(NO_PEOPLE)]

# All values are between 0 and 1 
boolean_c = [And([And([Or(dinner_schedule[r][h][p] ==0,dinner_schedule[r][h][p] == 1) 
                for p in range(NO_PEOPLE)])
                    for h in range(NO_HOUSES)])
                   for r in range(NO_ROUNDS)]

# A person is exactly in one house in each round.
one_house_at_a_time_c = [And([sum(dinner_schedule[r][h][p] for h in range(NO_HOUSES)) == 1
                              for p in range(NO_PEOPLE)])for r in range(NO_ROUNDS)]

# Precicely 5 people per occupied house.
five_people_per_house = [And([Or(sum(dinner_schedule[r][h]) == 5,sum(dinner_schedule[r][h]) == 0)
                          for h in range(NO_HOUSES)])
                         for r in range(NO_ROUNDS)]

# Each occupied house needs to have their couple in it.

# Each couple is in their house 2 times.

# A: Every two people among the 10 participants meet each other at least once.

# B: Every two people among the 10 participants meet each other at most 4 times.

# C: Couples never meet outside their own houses

# D: For every house the six guests (three for each of the two rounds) are distinct

# Solve the problem and print the model
s = Solver()
s.add(boolean_c + one_house_at_a_time_c + five_people_per_house)
res = s.check()
print(res)
m = s.model()
# print(m)
r = [[[m.evaluate(dinner_schedule[r][h][p]) for p in range(NO_PEOPLE)]
      for h in range(NO_HOUSES)]
     for r in range(NO_ROUNDS)]
for i in range(NO_ROUNDS):
    print("round:"+str(i))
    pp(r[i])
