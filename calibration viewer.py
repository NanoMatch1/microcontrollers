import csv


'''make a quick plot of calibration data'''

import matplotlib.pyplot as plt

# import files in data folder
import os
import sys
import numpy as np

dataDir = os.path.join(os.path.dirname(__file__), 'laser_calibration')
files = [f for f in os.listdir(dataDir) if f.endswith('.txt')]

dataDict = {}

fig, ax = plt.subplots(2,1)

for file in files:
    dataDict[file] = []
    with open(os.path.join(dataDir, file), 'r') as f:
        lines = f.readlines()
        data = []
        for line in lines:
            if line.startswith('#'):
                continue
            cols = line.split(',')
            data.append([float(cols[0]), float(cols[3])])
        dataDict[file] = np.array(data).astype(float)
        ax[0].scatter(dataDict[file][:, 0], dataDict[file][:, 1], label=file)
    
    '''fit a line to the data'''
    x = dataDict[file][:, 0]
    y = dataDict[file][:, 1]
    z = np.polyfit(x, y, 2)
    # get fit parameters
    p = np.poly1d(z)
    ax[0].plot(x, p(x), label='{} fit'.format(file))

    # plot residuals
    residuals = y - p(x)
    ax[1].plot(x, residuals, label='{} residuals'.format(file), marker='o')
    print(f'{file} fit: {z}')
    # ax[1].scatter(x, residuals)


plt.xlabel('Wavelength (nm)')
plt.ylabel('Steps L1')
plt.legend()
plt.show()

            