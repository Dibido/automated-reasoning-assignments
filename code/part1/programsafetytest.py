a = 1
b = 1

#b0_bTrue_1_bFalse_2_bTrue_3_bFalse_4_bFalse_5_bFalse_6 = 66,
#b0_bFalse_1_bTrue_2_bTrue_3_bTrue_4_bTrue_5_bFalse_6 = 66,
#b0_bFalvse_1_bFalse_2_bTrue_3_bTrue_4_bTrue_5_bTrue_6_bFalse_7_bTrue_8_bFalse_9_bFalse_10 =   701
list = [True, True, False, True, True, False, True, True, True, False]
list2 = [False, False, False, True, False, True, False, True, True, False]
#b0_bFalse_1_bTrue_2_bTrue_3_bFalse_4_bFalse_5_bFalse_6_bFalse_7_bFalse_8_bFalse_9_bFalse_10 = 701,
for i in range(1, 11):
    if list[i-1]:
        a = a+2*b
        b = b+i
    else:
        b = a+b
        a = a+i

print(a)
print(b)
