from z3 import *


NO_LOOPS = 10
list = []

for n in range(1,2):
    def f(a_prev,b_prev,i,a_prev_name,b_prev_name):
        if (i < NO_LOOPS+1):
            a1_name = a_prev_name + "_aTrue_"+ str(i)
            b1_name = b_prev_name + "_bTrue_"+ str(i)
            a2_name = a_prev_name + "_aFalse_"+ str(i)
            b2_name = b_prev_name + "_bFalse_"+ str(i)

            a1 = Int(a1_name)
            b1 = Int(b1_name)
            a2 = Int(a2_name)
            b2 = Int(b2_name)
            return Or(And(f(a1,b1,i+1,a1_name,b1_name),a1 == a_prev + 2*b_prev, b1 == b_prev +i ),And(f(a2,b2,i+1,a2_name,b2_name),a2 == a_prev +i,b2 == a_prev+b_prev))
        else:
            return b_prev == 700 + n

    a0 = Int("a0")
    b0 = Int("b0")
    not_crash_c = And(f(a0,b0,1,"a0","b0"),a0 == 1,b0 == 1)

    basic_c = [not_crash_c]

    # Solve the problem and print the model
    s = Solver()
    s.add(basic_c)
    res = s.check()
    print(str(n)+" "+str(res))

    if res == sat:
        m = s.model()
        #output = m.evaluate(not_crash_c)
        #print(output)
        #for item in m:
        #    print(item)
        #print(m)
        list.append(n)
    else:
        pass

print(list)