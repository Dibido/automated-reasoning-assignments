from z3 import *

A = DeclareSort('A')
B = DeclareSort('B')
C = DeclareSort('C')

p = Function('p', A, B, C, BoolSort())
q = Function('q', A, B, C, BoolSort())

dummyA = Const('dummyA', A)
dummyB = Const('dummyB', B)
dummyC = Const('dummyC', C)

def teaches(a, b):
    return Exists([dummyC], Or(p(a, b, dummyC), q(a, b, dummyC)))

constraint1 = ForAll([dummyB], Exists([dummyA], teaches(dummyA, dummyB)))

s = Solver()
s.add(constraint1)
print(s.check())
print(s.model())