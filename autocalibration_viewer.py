import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json



dataDir = os.path.join(os.path.dirname(__file__), 'autocalibration')
files = [f for f in os.listdir(dataDir) if f.endswith('.json')]

file = files[-1]

with open(os.path.join(dataDir, file), 'r') as f:
    data = json.load(f)

print(data)

dataDict = data

for wavelength, data in dataDict.items():
    data = np.array(data).astype(float)
    dataX = data[:, 0] 
    dataY = data[:, 1]
    plt.plot(dataX, dataY, label=wavelength)
    dataDict[wavelength] = data

plt.xlabel('steps')
plt.ylabel('Intensity')

plt.legend()
plt.show()
