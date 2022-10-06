from z3 import *

NO_LOOPS = 10
list = []

for n in range(1,11):
    variables = []

    # retruns a tuple (a,b) where a is the condition fo 700+n and b are the assignments of the variable sof the code. 
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
            
            f_true = f(a1,b1,i+1,a1_name,b1_name)
            f_false = f(a2,b2,i+1,a2_name,b2_name)

            return (Or(f_true[0],f_false[0]), And(a1 == a_prev + 2*b_prev, b1 == b_prev +i,a2 == a_prev +i,b2 == a_prev+b_prev,And(f_true[1]),And(f_false[1])))
        else:
            variables.append(b_prev)
            return (b_prev == 700 + n,True)

    a0 = Int("a0")
    b0 = Int("b0")
    not_crash_c = And(f(a0,b0,1,"a0","b0")[0],f(a0,b0,1,"a0","b0")[1],a0 == 1,b0 == 1)

    basic_c = [not_crash_c]

    # Solve the problem and print the model
    #c = Context()
    s = Solver()
    s.add(basic_c)
    res = s.check()
    print(str(n)+" "+str(res))

    if res == sat:
        m = s.model()
        for v in variables:
            if m.evaluate(v) == 700 + n:
                print("Crashing path for %d: %s" % ( n , v ))
    else:
        list.append(n)

print("Not crashing n : ")
print(list)