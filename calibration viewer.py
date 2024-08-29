import csv


'''make a quick plot of calibration data'''

'''eventually, create a calibration routine that goes to each wavelength and sweeps the laser frequency across the ccd. Collect spectra, peakfit, extract peak centre, and use to calibrate more efficiently.'''


'''
from most recent calibration
370-751 (delta 400 steps on l1) (558 (d 200))
857.44,,,-3473,405000,414
872.646,,,-4473,415000,152
pix_diff = 262 pix = 4.1793 nm

currently 410000,558

delta = 15.206/-1000 (nm_per_laser_steps)
15.206-4.1793 nm = 11.0267 nm
11.0267 nm/10000 steps on TRIAX = 0.00110267 nm/step
'''

import matplotlib.pyplot as plt

# import files in data folder
import os
import sys
import numpy as np

dataDir = os.path.join(os.path.dirname(__file__), 'laser_calibration')
files = [f for f in os.listdir(dataDir) if f.endswith('.txt')]

eept_file = os.path.join(os.path.dirname(__file__), 'eept.txt')

nm_per_pixel = 6.38064/400 # retrieved from recent calibration sweep
# nm_per_step = 0
triax_steps = 410000
nm_per_triax_step = 0.00110267

# absolute = 802.5-(643*nm_per_pixel)
# new = absolute + (nm_per_triax_step*(410000-375000)) + (nm_per_pixel*558)

calib_dict = {
    'nm_per_pixel': 6.38064/400, # retrieved from recent calibration sweep
    # nm_per_step = 0
    'triax_steps': 410000,
    'nm_per_triax_step': 0.00110267
}

laser_calibration = {}

def wavelength_calibration(wavelength_calibration, show=True):

    fig, ax = plt.subplots(3,1)

    for file in files:
        wavelength_calibration[file] = []
        with open(os.path.join(dataDir, file), 'r') as f:
            lines = f.readlines()
            data_set_1 = []
            data_set_2 = []
            for line in lines:
                if line.startswith('#'):
                    continue
                cols = line.split(',')
                data_set_1.append([float(cols[0]), float(cols[3])])
                data_set_2.append([float(cols[3]), float(cols[0])])
            wavelength_calibration[file] = (np.array(data_set_1).astype(float), np.array(data_set_2).astype(float))
            ax[0].scatter(wavelength_calibration[file][0][:, 0], wavelength_calibration[file][0][:, 1], label=file)
            ax[1].scatter(wavelength_calibration[file][1][:, 0], wavelength_calibration[file][1][:, 1], label=file)
        
        data_set_1
        '''fit a line to the data'''
        x1 = wavelength_calibration[file][0][:, 0]
        y1 = wavelength_calibration[file][0][:, 1]
        x2 = wavelength_calibration[file][1][:, 0]
        y2 = wavelength_calibration[file][1][:, 1]
        fit_scalars_1 = np.polyfit(x1, y1, 2)
        fit_scalars_2 = np.polyfit(x2, y2, 2)
        # get fit parameters
        p1 = np.poly1d(fit_scalars_1)
        p2 = np.poly1d(fit_scalars_2)
        ax[0].plot(x1, p1(x1), label='{} fit'.format(file))
        ax[1].plot(x2, p2(x2), label='{} fit'.format(file))

        # plot residuals
        residuals = y1 - p1(x1)
        ax[2].plot(x1, residuals, label='{} residuals'.format(file), marker='o')
        print(f'{file} fit_1: {fit_scalars_1}')
        print(f'{file} fit_2: {fit_scalars_2}')
        # ax[1].scatter(x, residuals)

    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Steps L1')
    plt.legend()
    if show is True:
        plt.show()

    return fit_scalars_1, fit_scalars_2

def process_eept(eept_file, plot_rows=[0,1,4,5]):
    cal_data = np.array(["L1", "L2", "NIU", "NIU", "G1", "G2", "NIU", "NIU", "triax_steps", "pixels"])
    with open(eept_file, 'r') as f:
        lines = f.readlines()

        for line in lines:
            data = []
            if line.startswith('#'):
                continue
            line = line.strip('\n')
            if len(line) == 0:
                continue
            try:
                set_avo, set_gary, set_triax = line.split(':')
            except Exception as e:
                print(e)
                print("check data file eept.txt")
                continue
    
            set_avo = set_avo.strip('[]')
            set_gary = set_gary.strip('[]')

            set_avo = set_avo.split(',')
            set_gary = set_gary.split(',')
            set_triax = set_triax.split(',')

            data.extend([*set_avo, *set_gary, *set_triax])
            # set_avo.extend(set_gary)
            # set_avo.extend(set_triax)
            new_data = []
            for x in data:
                value = float(x.strip("' XYZA"))
                new_data.append(value)
            # breakpoint()
            # print(new_data)
            cal_data = np.column_stack((cal_data, new_data))

    return cal_data.T
    # print(cal_data)
    # breakpoint()
            # breakpoint()


        # data = np.array(data).astype(float)
        # x = data[:, 0]
        # y = data[:, 1]
        # fit_scalars = np.polyfit(x, y, 2)
        # # get fit parameters
        # p = np.poly1d(fit_scalars)
        # plt.scatter(x, y)
        # plt.plot(x, p(x), label='fit')
        # plt.xlabel('Steps L1')
        # plt.ylabel('Steps L2')
        # plt.legend()
        # plt.show()
        # print(f'fit: {fit_scalars}')
        # return fit_scalars

def run_moror_calibration(cal_data, calib_dict, wavelength_calibration, show=True):
    # cal_data = process_eept(eept_file)
    # calibration_modes = [('L1', 'L2'), ('G1', 'G2'), ('Lx', 'Gx')]

    fig, ax = plt.subplots(3,1)

    sorted_data = cal_data[np.argsort(cal_data[:, 0])]
    breakpoint()
    data_l1 = np.sorted(cal_data[:, 0])
    data_l2 = cal_data[:, 1]



if __name__ == '__main__':
    wavelength_cal = wavelength_calibration(laser_calibration, show=False)
    
    # return a solution for a given value of x, fed to the calibration function
    # x = 0.5
    # y = p(x)
    # give it wavelength, get steps
    steps_from_nm = np.poly1d(wavelength_cal[0])
    sol = steps_from_nm(802.5) # 17.219 steps
    # print(sol)
    nm_from_steps = np.poly1d(wavelength_cal[1])
    # sol = nm_from_steps(227) # 799.1516 nm
    # sol = nm_from_steps(627) # 792.77096 nm # delta = 6.38064 nm
    # print(sol)


    # breakpoint()
    cal_data = process_eept(eept_file)
    run_moror_calibration(cal_data, calib_dict, wavelength_cal)

