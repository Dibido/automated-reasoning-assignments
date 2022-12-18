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

test_input = ["f(g(h(x))) ≻ h(f(x))"]

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
# pp(rules)
# Define ordering to find
test_symbols = ['f', 'g', 'h']
NO_SYMBOLS = len(test_symbols)
# symbols = ['a', 'b', 'c', 'd', 'f', 'g', 'h'] #, "x", "y", "z", "u", "v"] TODO: Do we need the ground terms?
# NO_SYMBOLS = len(symbols)
# encode the ordering using variables 〈f > g〉 for all f, g
ordering = [[ Bool('%s >= %s' % (i, j) ) for i in test_symbols ] for j in test_symbols ]
# pp(ordering)
# >= is reflexive (always f >= f).
ordering_c1 = [ And( [ ordering[i][j] == True for i in range(NO_SYMBOLS)  if i == j ] ) for j in range(NO_SYMBOLS)]
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
# for every relation # in { ≿ , > , = }, create a boolean variable〈a # b〉
# TODO implement the subterms instead of just terms
geq = [] # [ Bool('%s >= %s' % (l, r) ) for (l,r) in rules]
gt = [] # [ Bool('%s > %s' % (l, r) ) for (l,r) in rules]
eq = [] #[ Bool('%s = %s' % (l, r) ) for (l,r) in rules]
def get_function_subterms(rule, r):
    l = []
    for i in range(1,len(rule)):
        l.append(Bool('%s >= %s' % (rule[i], r)))
        if len(rule[i]) > 1:
            for j in range(1, len(rule[i])):
                l.append(get_function_subterms(rule[i], r))
    return l

def add_subterms(rule):
    l = rule[0] # get left
    r = rule[1] # get right
    if l[0] in test_symbols:
        geq.append(Bool('%s >= %s' % (l, r)))
        gt.append(Bool('%s > %s' % (l, r)))
        eq.append(Bool('%s = %s' % (l, r)))
        geq.extend(get_function_subterms(l, r))
        geq.extend(get_function_subterms(r, l))

for r in rules: # for all rules
    add_subterms(r)

pp(geq)

# TODO define >mul
# We say that A ≻mul B if we can write A = A1 ∪ A2, B = B1 ∪ B2, A2 is non-empty, A1 ≈match B1 and for all b ∈ B2 there is a ∈ A2 such that a ≻ b
def gtmul(rule):
    return True

# TODO define =match
# For two multisets A, B we say that A ≈match B if and only if we can write A = {{s1, . . . , sn}} and B = {{t1, . . . , tn}} and each si ≈ ti
# (note that we can order the elements of A and B in any way!).
def eqmatch(rule):
    # Create a multiset for both the subterms of s and t
    s = Multiset(rule[0])
    t = Multiset(rule[1])
    # Check if these multisets are equal
    return s == t

# 1. s ≿ t if and only if s ≻ t or s ≈ t
mpo_c1 = [ If(Or(gt[i] == True, eq[i] == True) , geq[i] == True, True) for i in range(len(rules)) ]

# 2. s ≻ t if and only if s = f(s1, . . . , sn) and at least one of the following holds:
    # (a) si ≿ t for some i ∈ {1, . . . , n}
    # (b) t = g(t1, . . . , tm) with f > g and s ≻ ti for all i ∈ {1, . . . , m}
    # (c) t = g(t1, . . . , tm) with f ≡ g and {{s1, . . . , sn}} ≻mul {{t1, . . . , tm}}
def mpo_c2a(rule):
    for sub in rule[0]:
        return True
        # if sub in test_symbols and geq[sub[0]]:
        #     return True
    return False

def mpo_c2b(rule):
    # if rule[1][0] in test_symbols and gt[i]: # t = g(t1, .., tm) and f > g
    #     for sub in rule[1]:
    #         if sub not in test_symbols:
    #             return False
    return True

def mpo_c2c(rule):
    return True

mpo_c2 = [ If((And(rules[i][0][0] in test_symbols , Or(mpo_c2a(rules[i]), mpo_c2b(rules[i]), mpo_c2c(rules[i])))), gt[i] == True ,True) for i in range(NO_RULES) ]

#3. s ≈ t if and only if one of the following holds:
    #(a) s and t are both the same variable;
    #(b) s = f(s1, . . . , sn) and t = g(t1, . . . , tn) and f ≡ g and {{s1, . . . , sn}} ≈match {{t1, . . . , tn}}
def mpo_c3a(rule):
    return rule[0] == rule[1]

def mpo_c3b(rule):
    return True

mpo_c3 = [ If(Or( mpo_c3a(rules[i]), mpo_c3b(rules[i]) ), eq[i] == True, True) for i in range(NO_RULES) ]

# TODO require that top level inequalities hold (the rules)
mpo_c4 = [ ]

constraints = ordering_c1 + ordering_c2 + ordering_c3 + mpo_c1 + mpo_c2 + mpo_c3 + mpo_c4

s = Solver()
s.add(constraints)
res = s.check()
print(res)
if res == sat:
    m = s.model()
    # pp(m)