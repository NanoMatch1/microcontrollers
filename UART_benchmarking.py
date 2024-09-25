import numpy as np
import matplotlib.pyplot as plt
import os

scriptDir = os.path.dirname(__file__)

data_25 = [[0.01, 0.2045206069946289], [0.02, 0.2053760051727295], [0.04, 0.20750126838684083], [0.08, 0.2182542324066162], [0.128, 0.26523077487945557], [0.16, 0.298358154296875], [0.256, 0.39398369789123533], [0.32, 0.4576232671737671], [0.512, 0.6500587224960327], [0.64, 0.7792911767959595], [1.024, 1.1614389181137086]]

data_96 = [[0.01, 0.21094768047332763], [0.02, 0.2201913118362427], [0.04, 0.24236199855804444], [0.08, 0.27793006896972655], [0.128, 0.33017377853393554], [0.16, 0.35918378829956055], [0.256, 0.4597161054611206], [0.32, 0.5198859930038452], [0.512, 0.7104912519454956], [0.64, 0.8398773670196533], [1.024, 1.2268903255462646]]

data_25 = np.array(data_25).astype(float)
data_96 = np.array(data_96).astype(float)

fig, ax = plt.subplots(1, 2)

ax[0].plot(data_25[:,0], data_25[:,1], label='25', marker='o')
ax[0].plot(data_96[:,0], data_96[:,1], label='96', marker='o')

ax[0].set_xlabel('Time requested (s)')
ax[0].set_ylabel('Time actual taken (s)')
ax[0].set_title('Time taken')
ax[0].legend()

overhead_25 = data_25[:,1] - data_25[:,0]
overhead_96 = data_96[:,1] - data_96[:,0]

ax[1].plot(data_25[:,0], overhead_25, label='25', marker='o')
ax[1].plot(data_96[:,0], overhead_96, label='96', marker='o')

ax[1].set_xlabel('Time requested (s)')
ax[1].set_ylabel('Overhead (s)')
ax[1].legend()
ax[1].set_title('Overhead - calculated on V0.1 25/09/24')

data_25 = np.column_stack((data_25, overhead_25))
data_25 = np.vstack((['Time requested (s)', 'Time actual taken (s)', '250000 Overhead (s)'], data_25))
data_96 = np.column_stack((data_96, overhead_96))
data_96 = np.vstack((['Time requested (s)', 'Time actual taken (s)', '9600 Overhead (s)'], data_96))

# breakpoint()

filename = os.path.join(scriptDir, 'benchmark', 'overhead_25-09-24.csv')

plt.savefig(os.path.join(scriptDir, 'benchmark', 'overhead_25-09-24.png'))
np.savetxt(filename, np.array(np.column_stack((data_25, data_96))), fmt='%s', delimiter=',', newline='\n')

plt.show()
