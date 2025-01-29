steps=[0,2120,0,0]
backlash_correction = [-20 if i != 0 else 0 for i in steps]
print(backlash_correction)