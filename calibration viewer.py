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

calibration_records = {
    'date': '2024-08-27'
    ,

    'manual_measurements': {
        'nm_per_pixel': 6.38064/400, # retrieved from recent calibration sweep
        # nm_per_step = 0
        'triax_steps': 410000,
        'nm_per_triax_step': 0.00110267
    },

    'eept': {
        'headers': {
            'L1': 0,
            'L2': 1,
            'NIU': 2,
            'NIU': 3,
            'G1': 4,
            'G2': 5,
            'NIU': 6,
            'NIU': 7,
            'triax_steps': 8,
            'pixels': 9
        },
        'data':
            "['X-473', 'Y212', 'Z0', 'A0']:['X58', 'Y45', 'Z0', 'A0']:380000,518\n['X-973', 'Y424', 'Z0', 'A0']:['X112', 'Y90', 'Z0', 'A0']:385000,390\n['X-1473', 'Y636', 'Z0', 'A0']:['X184', 'Y170', 'Z0', 'A0']:390000,263\n['X-2473', 'Y1058', 'Z0', 'A0']:['X350', 'Y359', 'Z0', 'A0']:395000,645\n['X-3473', 'Y1479', 'Z0', 'A0']:['X508', 'Y587', 'Z0', 'A0']:405000,414\n['X-4473', 'Y1897', 'Z0', 'A0']:['X619', 'Y698', 'Z0', 'A0']:415000,152\n['X-5473', 'Y2327', 'Z0', 'A0']:['X770', 'Y851', 'Z0', 'A0']:420000,542\n['X-6473', 'Y2735', 'Z0', 'A0']:['X917', 'Y970', 'Z0', 'A0']:430000,300\n['X-7473', 'Y3149', 'Z0', 'A0']:['X1023', 'Y1064', 'Z0', 'A0']:435000,668\n['X-8473', 'Y3572', 'Z0', 'A0']:['X1163', 'Y1181', 'Z0', 'A0']:445000,436\n['X27', 'Y1', 'Z0', 'A0']:['X-28', 'Y-28', 'Z0', 'A0']:375000,646\n['X1027', 'Y-413', 'Z0', 'A0']:['X-198', 'Y-224', 'Z0', 'A0']:370000,274\n['X2027', 'Y-846', 'Z0', 'A0']:['X-323', 'Y-343', 'Z0', 'A0']:360000,489\n['X3027', 'Y-1262', 'Z0', 'A0']:['X-468', 'Y-455', 'Z0', 'A0']:355000,140\n['X4027', 'Y-1687', 'Z0', 'A0']:['X-603', 'Y-566', 'Z0', 'A0']:345000,367\n#['X5027', 'Y-2186', 'Z0', 'A0']:['X-693', 'Y-650', 'Z0', 'A0']:335000,589\n#['X6027', 'Y-2609', 'Z0', 'A0']:['X-848', 'Y-782', 'Z0', 'A0']:330000,242\n#['X7027', 'Y-3045', 'Z0', 'A0']:['X-963', 'Y-888', 'Z0', 'A0']:320000,473\n#['X-473', 'Y168', 'Z0', 'A0']:['X62', 'Y50', 'Z0', 'A0']:380000,515"
    }
}

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

    headers = cal_data.T[0, :]
    cal_data = cal_data.T[1:, :].astype(float)

    return headers, cal_data
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

def run_moror_calibration(headers, cal_data, calib_dict, wavelength_calibration, show=True):
    # cal_data = process_eept(eept_file)
    # calibration_modes = [('L1', 'L2'), ('G1', 'G2'), ('Lx', 'Gx')]
    # print(wavelength_calibration)
    # breakpoint()
    calibrations = {}

    nm_per_laser_steps = np.poly1d(wavelength_calibration[1])

    fig, ax = plt.subplots(3,1)

    sorted_data = cal_data[np.argsort(cal_data[:, 0])]
    # breakpoint()
    data_l1 = sorted_data[:, 0]
    data_l2 = sorted_data[:, 1]
    data_g1 = sorted_data[:, 4]
    data_g2 = sorted_data[:, 5]

    wavelength_axis = nm_per_laser_steps(data_l1)
    spectrometer_position = []
    for x in range(len(cal_data[:, 8])):
        wavelength = wavelength_axis[x]
        spectrometer_steps = cal_data[x, 8]
        pixel_number = cal_data[x, 9]
        wavelength_from_50 = calib_dict['nm_per_pixel']*(50-pixel_number)
        triax_steps_to_shift_lambda = spectrometer_steps - (wavelength_from_50/calib_dict['nm_per_triax_step'])
        spectrometer_position.append(triax_steps_to_shift_lambda)
    
    print(spectrometer_position)
    breakpoint()    



    new_data_array = np.column_stack((wavelength_axis, data_l1, data_l2, data_g1, data_g2))
    print(wavelength_axis)
    breakpoint()
    fit_coeff_laser = np.polyfit(data_l1, data_l2, 1)
    fit_coeff_grating = np.polyfit(data_g1, data_g2, 1)
    ax[0].scatter(data_l1, data_l2, label='L1 vs L2')
    ax[1].scatter(data_g1, data_g2, label='G1 vs G2')

    

    # fit a line to the data

    # get fit parameters
    p_laser = np.poly1d(fit_coeff_laser)
    p_grating = np.poly1d(fit_coeff_grating)

    ax[0].plot(data_l1, p_laser(data_l1), label='L1 vs L2 fit', color='tab:purple')
    ax[1].plot(data_g1, p_grating(data_g1), label='G1 vs G2 fit', color='tab:purple')

    # plot residuals
    residuals_l = data_l2 - p_laser(data_l1)
    residuals_g = data_g2 - p_grating(data_g1)
    ax[2].plot(data_l1, residuals_l, label='L1 vs L2 residuals', marker='o')
    ax[2].plot(data_l1, residuals_g, label='G1 vs G2 residuals', marker='o')

    ax[0].legend()
    ax[1].legend()
    ax[2].legend()
    
    if show is True:
        plt.show()

    print(f'l1xl2 fit: {fit_coeff_laser}')
    print(f'g1xg2 fit: {fit_coeff_grating}')
    
    wavelength_cal_laser = np.poly1d(wavelength_axis, data_l1, 1)
    wavelength_cal_grating = np.poly1d(wavelength_axis, data_g1, 1)

    fig, ax = plt.subplots(3,1)
    ax[0].scatter(wavelength_axis, data_l1, label='Lambda L1')
    ax[1].scatter(wavelength_axis, data_g1, label='Lambda G1')


    # residuals
    



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
    headers, cal_data = process_eept(eept_file)
    run_moror_calibration(headers, cal_data, calib_dict, wavelength_cal)

