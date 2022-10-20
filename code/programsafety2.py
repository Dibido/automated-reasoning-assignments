import itertools
from z3 import *

NO_ROUNDS = 11 # (including 0 state so for 10 loops 11 rounds)

# index mapping for easy visualisation
a = 0
b = 1
i = 2
bo = 3
NO_ELEMENTS = 4

list = []

for n in range(1,11):
    iterrations = [[Int("R%s_H%s" % (r, e))
                        for e in range(NO_ELEMENTS)]
                    for r in range(NO_ROUNDS)]

    # initial state, the boolean is 77 as not to confuse it.
    init_c = [And(iterrations[0][a] == 1 , iterrations[0][b] == 1 , iterrations[0][i] == 1 , iterrations[0][bo] == 77)]

    # check if the previous state corresponds wirt either case for the boolean.
    basic_c = [ Or(And(iterrations[l+1][a] == iterrations[l][a] + 2 * iterrations[l][b],iterrations[l+1][b] == iterrations[l][b] +iterrations[l][i],iterrations[l+1][i] == iterrations[l][i]+1,iterrations[l+1][bo] == 1 ),
                        And(iterrations[l+1][a] == iterrations[l][a] +  iterrations[l][i],iterrations[l+1][b] == iterrations[l][a] +iterrations[l][b],iterrations[l+1][i] == iterrations[l][i]+1,iterrations[l+1][bo] == 0 )) for l in range(NO_ROUNDS-1)]

    # check the goal
    final_c = [iterrations[NO_ROUNDS-1][b] == 700+n]

    # optimisation to check that b is always smaller than the goal, allows trowing out items faster.
    optimise_final_c = [ iterrations[r][b] <= 700+n for r in range(NO_ROUNDS) ]

    # Solve the problem and print the model
    s = Solver()
    s.add(basic_c + init_c + final_c)
    #s.add(basic_c + init_c + final_c + optimise_final_c)
    res = s.check()

    print("for n =" + str(n))
    if res == sat:
        m = s.model()
        # print(m)
        r = [[[m.evaluate(iterrations[r][e])]
            for e in range(NO_ELEMENTS)]
            for r in range(NO_ROUNDS)]
        for j in range(NO_ROUNDS):
            print("round:"+str(j))
            pp(r[j])
    else:
        print("unsat")
        list.append(n)

print (list)