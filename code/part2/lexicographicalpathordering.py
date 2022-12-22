from z3 import *
from multiset import *
import parsley

# Parse the terms for the TRS
rules_input = ["c(x, y, u, v) ≻ b(f(x, y), b(u, u, u), g(v, b(x, y, u)))",
                "b(f(x, y), g(x, y), f(x, g(z, u))) ≻ b(f(x, z), y, g(g(g(y, x), x), x))",
                "h(g(x, g(u, z)), c(x, y, x, z)) ≻ f(d(x, z), u)",
                "h(d(f(x, y), g(u, v)), f(x, y)) ≻ f(c(u, x, v, y), g(y, x))",
                "f(b(x, y, z), u) ≻ h(u, f(x, h(y, x)))",
                "b(a(x, y, z), y, x) ≻ c(x, x, y, x)",
                ]

test_input = ["f(g(x)) ≻ g(f(x))"]

parse_rules = """
symbol = <letter>
func = f1 | f2 | f3 | f4
f1 = symbol:f'('term:x')' -> [f, x]
f2 = symbol:f'('term:x', 'term:y')' -> [f, x ,y]
f3 = symbol:f'('term:x', 'term:y', 'term:z')' -> [f,x,y,z]
f4 = symbol:f'('term:x', 'term:y', 'term:z', 'term:u')' -> [f,x,y,z,u]
term = ( func | symbol )
terms = func:l ' ≻ ' func:r -> (l, r)
"""

Grammar = parsley.makeGrammar(parse_rules, {})
rules = []
for r in test_input:
    rule = Grammar(r)
    rules.append(rule.terms())
NO_RULES = len(rules)

#==========================================================================================

# pp(rules)
# Define ordering to find
test_symbols = ['f', 'g']
NO_SYMBOLS = len(test_symbols)

# symbols = ['a', 'b', 'c', 'd', 'f', 'g', 'h'] #, "x", "y", "z", "u", "v"] TODO: Do we need the ground terms?
# NO_SYMBOLS = len(symbols)

# TODO: Is this ordering still needed?
# encode the ordering using variables 〈f > g〉 for all f, g
ordering = [[ Bool('%s_>_%s' % (i, j) ) for i in test_symbols ] for j in test_symbols ]
# pp(ordering)
# pp(ordering)
#require: ¬〈f > f〉 for all f
ordering_c1 = [ And( [ ordering[i][j] == False for i in range(NO_SYMBOLS)  if i == j ] ) for j in range(NO_SYMBOLS)]
# pp(ordering_c1)
# require: 〈f > g〉 ↔ ¬〈g > f〉 for all f, g with f /= g
ordering_c2 = []
for f in range(NO_SYMBOLS):
    for g in range(NO_SYMBOLS):
        if f != g: # Not f > f
            ordering_c2.append(If(ordering[f][g] == True ,ordering[g][f] == False, True))
# pp(ordering_c2)
# require: 〈f > g〉 ∧ 〈g > h〉 → 〈f > h〉 for all f, g, h
# >= is transitive (if f > g > h then f > h)
ordering_c3 = []
for i in range(NO_SYMBOLS):
    for j  in range(NO_SYMBOLS):
        if i != j: # not f > f
            ordering_c3.append(And ([If (And (ordering[i][j] == True, ordering[k][i] == True), ordering[k][j] == True, True) for k in range(NO_SYMBOLS) if k != i and k != j ] ) )
# pp(ordering_c3)
# for the subterms a and b in s and t:
# for every relation # in {LPO, sub, copy, lex}, create a boolean variable〈a # b〉
# TODO check if we have all subterms
lpo = []
lpo_sub = []
lpo_copy = []
lpo_lex = []

def get_function_subterms(rule, r, comp):
    l = []
    for i in range(1,len(rule)):
        # TODO allow for adding the proper inequality names, aka >LPO/>SUB/>COPY/>LEX
        l.append(Bool(('%s_'+comp+'_%s') % (str(rule[i]).replace(" ","_"), str(r).replace(" ","_"))))
        if len(rule[i]) > 1:
            for _ in range(1, len(rule[i])):
                l.append(get_function_subterms(rule[i], r, comp))
    return l

def add_subterms(rule):
    l = rule[0] # get left
    r = rule[1] # get right
    if l[0] in test_symbols:
        lpo.append(Bool('%s_>LPO_%s' % (str(l).replace(" ","_"), str(r).replace(" ","_"))))
        lpo_sub.append(Bool('%s_>SUB_%s' % (str(l).replace(" ","_"), str(r).replace(" ","_"))))
        lpo_copy.append(Bool('%s_>COPY_%s' % (str(l).replace(" ","_"), str(r).replace(" ","_"))))
        lpo_lex.append(Bool('%s_>LEX_%s' % (str(l).replace(" ","_"), str(r).replace(" ","_"))))
        lpo.extend(get_function_subterms(l, r, ">LPO"))
        lpo.extend(get_function_subterms(r, l, ">LPO"))
        lpo_sub.extend(get_function_subterms(l, r, ">SUB"))
        lpo_sub.extend(get_function_subterms(r, l, ">SUB"))
        lpo_copy.extend(get_function_subterms(r, l, ">COPY"))
        lpo_copy.extend(get_function_subterms(r, l, ">COPY"))
        lpo_lex.extend(get_function_subterms(l, r, ">LEX"))
        lpo_lex.extend(get_function_subterms(r, l, ">LEX"))

for r in rules: # for all rules
    add_subterms(r)

pp(lpo)
pp("====================")
pp(lpo_sub)

NO_TERMS = len(lpo)

#==========================================================================================

# TODO For each variable 〈a # b〉 we now require the defining formula.
# TODO Problem: comparing the a and b and then setting the proper boolean
#       Need to use the original rules and check current booleans to set new booleans

# TODO if a = b, then ¬〈a # b〉 for all # ∈ {LPO, sub, copy, lex}
lpo_c1 = [If(True , And(lpo[i] == False, lpo_sub[i] == False, lpo_copy[i] == False, lpo_lex[i] == False) , True) for i in range(NO_TERMS)]

# TODO otherwise, if a is a variable: ¬〈a # b〉 for all # ∈ {LPO, sub, copy, lex}
lpo_c2 = [If(True, And(lpo[i] == False, lpo_sub[i] == False, lpo_copy[i] == False, lpo_lex[i] == False), True) for i in range(NO_TERMS)]

# otherwise, if a = f(a1, . . . , an):
# TODO  〈a LPO b〉 ↔ 〈a LPOsub  b〉 ∨ 〈a LPOcopy b〉 ∨ 〈a LPOlex b〉
lpo_c3a = [ If(Or(lpo_sub[i] == True, lpo_copy[i] == True, lpo_lex[i] == True) , lpo[i] == True , True) for i in range(NO_TERMS) ]
# TODO  〈a subLPO b〉 ↔ 〈a1 LPO b〉 ∨ . . . ∨ 〈an LPO b〉   
lpo_c3b = []

#If b = f(b1, . . . , bn), and i is the lowest index such that ai /= bi, then:
    # TODO ¬〈a copyLPO b〉
lpo_c4a = []
    # TODO〈a lexLPO b〉 ↔ 〈a LPO b1〉 ∧ . . . ∧ 〈a LPO bn〉 ∧ 〈ai > bi〉
lpo_c4b = []

# otherwise, if b = g(b1, . . . , bm) with f /= g then:
    # TODO〈a copyLPO b〉 ↔ 〈f > g〉 ∧ 〈a LPO b1〉 ∧ . . . ∧ 〈a LPO bm〉
lpo_c5a = []
    # TODO ¬〈a lex LPO b〉
lpo_c5b = []

# TODO otherwise if b is a variable, ¬〈a # b〉 for # ∈ {copy LPO, lex LPO}
lpo_c6 = []

# TODO Also require that top level inequalities hold (the rules)
lpo_c7 = [lpo[i] == True for i in range(0,NO_RULES)]

ordering_c = ordering_c1 + ordering_c2 + ordering_c3
lpo_c = lpo_c1 + lpo_c2 + lpo_c3a + lpo_c3b + lpo_c4a + lpo_c4b + lpo_c5a + lpo_c5b  + lpo_c6 + lpo_c7
constraints = ordering_c + lpo_c

#==========================================================================================

s = Solver()
s.add(constraints)
res = s.check()
print(res)
if res == sat:
    m = s.model()
    pp(m)
