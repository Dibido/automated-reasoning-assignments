from z3 import *

# used for summing booleans


def boolListToInt(l):
    return If(l, 1, 0)


def sumBool(l):
    return sum(map(boolListToInt, l))


NO_ROUNDS = 5
NO_HOUSES = 5
NO_PEOPLE = 10

dinner_schedule = [[[Bool("R%s_H%s_P%s" % (r, h, p))  # could not use bool since sum does not take bools.
                     for p in range(NO_PEOPLE)]
                    for h in range(NO_HOUSES)]
                   for r in range(NO_ROUNDS)]

person_to_house_index = [p//(NO_PEOPLE//NO_HOUSES) for p in range(NO_PEOPLE)]

# A person is exactly in one house in each round.
one_house_at_a_time_c = [And([(sum(If(dinner_schedule[r][h][p], 1, 0) for h in range(NO_HOUSES)) == 1)
                              for p in range(NO_PEOPLE)])for r in range(NO_ROUNDS)]

# Precicely 5 people per occupied house, implies only 2 houses are occupied.
five_people_per_house_c = [And([Or(sumBool(dinner_schedule[r][h]) == 5, sumBool(dinner_schedule[r][h]) == 0)
                                for h in range(NO_HOUSES)])
                           for r in range(NO_ROUNDS)]

# Each occupied house needs to have their couple in it.
# TODO: better way to specify people based on house than h*2 and h*2+1
each_house_its_couple_c = [And([Or(And(dinner_schedule[r][h][h*2], dinner_schedule[r][h][h*2+1]), sumBool(dinner_schedule[r][h]) == 0)
                                for h in range(NO_HOUSES)])
                           for r in range(NO_ROUNDS)]

# Each couple is in their house exactly 2 times.
two_times_in_own_house_c = [sum(If(dinner_schedule[r][person_to_house_index[p]][p], 1, 0) for r in range(NO_ROUNDS)) == 2
                            for p in range(NO_PEOPLE)]

# Every two people among the 10 participants meet each other at most 4 times during these 5 rounds.
at_most_four_c = []
for p in range(NO_PEOPLE):
     for p2 in range(NO_PEOPLE):
          if(p < p2):
               at_most_four_c.append(sumBool([Or([And(dinner_schedule[r][h][p], dinner_schedule[r][h][p2]) for h in range(NO_HOUSES)]) for r in range(NO_ROUNDS)]) <= 4)
                  
basic_c = one_house_at_a_time_c + five_people_per_house_c + each_house_its_couple_c + two_times_in_own_house_c + at_most_four_c
# A: Every two people among the 10 participants meet each other at least once.
# for each player: check if it shares any home and round with every other player (including itself which is by definition true.)

a_c = []
for p in range(NO_PEOPLE):
     for p2 in range(NO_PEOPLE):
          if(p < p2): a_c.append(Or([Or([And(dinner_schedule[r][h][p], dinner_schedule[r][h][p2]) for h in range(NO_HOUSES)]) for r in range(NO_ROUNDS)]))

# B: Every two people among the 10 participants meet each other at most 3 times.

b_c = []
for p in range(NO_PEOPLE):
     for p2 in range(NO_PEOPLE):
          if(p < p2):
               b_c.append(sumBool([Or([And(dinner_schedule[r][h][p], dinner_schedule[r][h][p2]) for h in range(NO_HOUSES)]) for r in range(NO_ROUNDS)]) <= 3)

# C: Couples never meet outside their own houses
c_c = []
for c in range(NO_HOUSES):
     p1 = c*2
     p2 = c*2+1
     for h in range(NO_HOUSES):
          if( h != c):
               c_c.append(And([Not(And(dinner_schedule[r][h][p1],dinner_schedule[r][h][p2])) for r in range(NO_ROUNDS)]))

# D: For every house the six guests (three for each of the two rounds) are distinct
d_c = []
for h in range(NO_HOUSES):
     for p in range(NO_PEOPLE):
          if(person_to_house_index[p] != h): # person not in own house
               d_c.append(sumBool([dinner_schedule[r][h][p] for r in range(NO_ROUNDS)]) < 2)

# Solve the problem and print the model
s = Solver()
#s.add(basic_c + a_c + c_c) # Possible with a + c
#s.add(basic_c + a_c + d_c)  # Possible with a + d
#s.add(basic_c + a_c + c_c + d_c) # Impossible with a + c + d
s.add(basic_c + b_c + c_c + d_c) # Possible with b + c + d
res = s.check()
pp(res)

if res == sat:
    m = s.model()
    # print(m)
    r = [[[m.evaluate(If(dinner_schedule[r][h][p], 1, 0)) for p in range(NO_PEOPLE)]
          for h in range(NO_HOUSES)]
         for r in range(NO_ROUNDS)]
    for i in range(NO_ROUNDS):
        print("round:"+str(i))
        pp(r[i])
