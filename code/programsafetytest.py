a = 1
b = 1
# b0_
# b1_1_
# b2_2_
# b1_3_
# b1_4_
# b1_5_
# b1_6_
# b2_7_
# b2_8_
# b2_9_
# b1_10 = 710
list = [False,True,True,True,False,True,False,True,True,False]
 #b0_b1_1_b1_2_b1_3_b2_4_b2_5_b1_6_b2_7_b1_8_b1_9_b1_10 = 701,
 #b0_b1_1_b1_2_b2_3_b1_4_b2_5_b2_6_b1_7_b1_8_b2_9_b2_10 = 701,
 #b0_b1_1_b1_2_b1_3_b2_4_b2_5_b2_6_b1_7_b2_8_b1_9_b1_10 = 701,
list.reverse()
#b0_bFalse_1_bTrue_2_bFalse_3_bFalse_4_bTrue_5_bTrue_6_bTrue_7_bTrue_8_bTrue_9_bFalse_10 = 704,
list = [False, True, False, False, True, True, True, True, True, False]
print(len(list))
print(list)
 # b0_bFalse_1_bTrue_2_bTrue_3_bTrue_4_bFalse_5_bTrue_6_bFalse_7_bTrue_8_bTrue_9_bFalse_10 = 701,
for i in range(1,11):
    if list[i-1]:
        a = a+2*b
        b = b+i
    else:
        b = a+b
        a = a+i

print(a)
print(b)