import matplotlib.pyplot as plt

# import files in data folder
import os
import sys
import numpy as np
# sys.path.append(os.path.join(os.path.dirname(__file__), 'data'))
# from data import data

dataDir = os.path.join(os.path.dirname(__file__), 'data')
files = [f for f in os.listdir(dataDir) if f.endswith('.txt')]
files = [f for f in files if 'motor' in f][5:]

print(files)

# breakpoint()

for file in files:
    with open(os.path.join(dataDir, file), 'r') as f:
        lines = f.readlines()
        try:
            print(file)
            x = [float(line.split(',')[0]) for line in lines]
            x = range(len(x))
            # x = np.array(x).astype(float)/max(x)

            y = [float(line.split(',')[1]) for line in lines]
            plt.plot(x, y, label=file)

        except:
            x = [float(line.split()[0]) for line in lines]
            x = range(len(x))
            # x = np.array(x).astype(float)/max(x)
            y = [float(line.split()[1]) for line in lines]
            plt.plot(x, y, label=file)
        # plt.plot(x, y, label=file)

plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity')
plt.legend()
plt.show()