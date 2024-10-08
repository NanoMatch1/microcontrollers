import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

dataDir = os.path.join(os.path.dirname(__file__), 'autocalibration')
files = [f for f in os.listdir(dataDir) if f.endswith('.json')]
# files = files.sort(lambda x: int(x[:-4].split('_')[1:]))
# sort with the number in the filename
files.sort(key=lambda x: int(x[:-5].split('_')[1]))

with open(os.path.join(dataDir, files[-1]), 'r') as f:
    data = json.load(f)


# print(data)

# for wavelength, data in data.items():
#     data = np.array(data).astype(float)
#     dataX = data[:, 0] 
#     dataY = data[:, 1]
#     plt.plot(dataX, dataY, label=wavelength)

# plt.legend()
# plt.show()
print(len(next(iter(data.values()))))
newData = np.empty((0, len(next(iter(data.values())))))
for wavelength, data in data.items():
    # data = np.array(data).astype(float)
    print(len(data))
    column = [wavelength, data]
    newData = np.vstack((newData, column))

print(newData)
