import csv
import json


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
        'nm_per_laser_step': 0.0158,
        'lamba_change_for_400_steps': 6.32,
        'nm_per_pixel': 4/400, # retrieved from recent calibration sweep
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

# nm_per_pixel = 6.38064/400 # retrieved from recent calibration sweep
# # nm_per_step = 0
# triax_steps = 375000
# nm_per_triax_step = 0.00110267

# absolute = 802.5-(643*nm_per_pixel)
# new = absolute + (nm_per_triax_step*(410000-375000)) + (nm_per_pixel*558)

#662/469

#731.162-734.432 = -3.27 nm
#-3.27nm/200steps = -0.01635 nm/step
#293-660pix=-367
#0.0168557nm/pix*-367pix = -6.186 nm/3000 steps triax
# -0.002062 nm/step triax


calib_dict = {
    'pixels_per_laser_step': -194/200,
    'nm_per_laser_step': -0.01635,
    'nm_per_pixel': -0.01635/-0.97, #0.0168557

    # 'nm_per_pixel': -6.32/400, # retrieved from recent calibration sweep
    # nm_per_step = 0
    'triax_steps': 375000,
    'nm_per_triax_step': -0.002062
}

laser_calibration = {}

def r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)  # Residual sum of squares
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)  # Total sum of squares
    return 1 - (ss_res / ss_tot)

def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def mae(y_true, y_pred):
    return np.mean(np.abs(y_true - y_pred))

def residual_std(residuals):
    return np.std(residuals)

def adjusted_r_squared(y_true, y_pred, p):
    n = len(y_true)
    r2 = r_squared(y_true, y_pred)
    return 1 - (1 - r2) * (n - 1) / (n - p - 1)


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
            new_data = []
            for x in data:
                value = float(x.strip("' XYZA"))
                new_data.append(value)

            cal_data = np.column_stack((cal_data, new_data))

    headers = cal_data.T[0, :]
    cal_data = cal_data.T[1:, :].astype(float)

    return headers, cal_data


def run_motor_calibration(headers, cal_data, calib_dict, wavelength_calibration, show=True):

    calibrations = {}
    report_dict = {}


    fig, ax = plt.subplots(3,1)

    sorted_data = cal_data[np.argsort(cal_data[:, 0])]
    # breakpoint()
    data_l1 = sorted_data[:, 0]
    data_l2 = sorted_data[:, 1]
    data_g1 = sorted_data[:, 4]
    data_g2 = sorted_data[:, 5]

    nm_per_laser_steps = np.poly1d(wavelength_calibration[1])
    wavelength_axis = nm_per_laser_steps(data_l1)


    def calculate_triax_steps(sorted_data, wavelength_axis, calib_dict,):
        '''Perparatory calculation. Calculates the correct number of steps for each wavelength in the calibration data to be at pixel 50 on the spectrometer'''

        spectrometer_position = []
        # spectrometer_adjustment = []

        spectrometer_steps = sorted_data[:, 8]
        pixel_number = sorted_data[:, 9]

        for idx, steps in enumerate(spectrometer_steps):
            wavelength = wavelength_axis[idx]
            pixel = pixel_number[idx]
            wavelength_from_50 = calib_dict['nm_per_pixel']*(50-pixel)
            triax_steps_to_shift = wavelength_from_50/calib_dict['nm_per_triax_step']
            print(pixel, triax_steps_to_shift, steps, wavelength)
            triax_actual_steps = steps + (wavelength_from_50/calib_dict['nm_per_triax_step'])
            spectrometer_position.append(triax_actual_steps)

        return spectrometer_position
    

    spectrometer_position = calculate_triax_steps(sorted_data, wavelength_axis, calib_dict)

    def wavelength_to_triax(spectrometer_position, wavelength_axis, show=True):
        '''Calibration for using laser wavelength to calculate spectrometer position in TRIAX steps. '''
        
        triax_steps = np.polyfit(wavelength_axis, spectrometer_position, 2)
        p_triax_steps = np.poly1d(triax_steps)
        
        y_pred = p_triax_steps(wavelength_axis)
        residuals = spectrometer_position - y_pred

        # Fit quality metrics
        r2 = r_squared(spectrometer_position, y_pred)
        rmse_val = rmse(spectrometer_position, y_pred)
        mae_val = mae(spectrometer_position, y_pred)
        res_std = residual_std(residuals)

        if show is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(wavelength_axis, spectrometer_position, label='Triax Steps')
            ax[0].plot(wavelength_axis, y_pred, label=f'Triax Steps fit (R2={r2:.8f})', color='tab:purple')
            ax[1].plot(wavelength_axis, residuals, label='Triax Steps residuals', marker='o')
            ax[0].set_title('Wavelength to Triax Steps')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        print(f"R2: {r2:.4f}, RMSE: {rmse_val:.4f}, MAE: {mae_val:.4f}, Residual Std: {res_std:.4f}")

        return triax_steps

    # Use the updated function
    triax_steps = wavelength_to_triax(spectrometer_position, wavelength_axis, show=True)
    calibrations['wl_triax_steps'] = triax_steps.tolist()


    def triax_steps_to_wavelength(spectrometer_position, wavelength_axis, show=True):
        '''Reverse calibration for calculating laser wavelength from spectrometer position in TRIAX steps.'''

        steps_to_wavelength = np.polyfit(spectrometer_position, wavelength_axis, 2)
        p_steps_to_wavelength = np.poly1d(steps_to_wavelength)

        y_pred = p_steps_to_wavelength(spectrometer_position)
        residuals = wavelength_axis - y_pred
        residuals_scaled = (residuals/wavelength_axis) * 100

        # Fit quality metrics
        r2 = r_squared(wavelength_axis, y_pred)
        rmse_val = rmse(wavelength_axis, y_pred)
        mae_val = mae(wavelength_axis, y_pred)
        res_std = residual_std(residuals)


        if show is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(spectrometer_position, wavelength_axis, label='Wavelength')
            ax[0].plot(spectrometer_position, y_pred, label=f'Wavelength fit (R2={r2:.8f})', color='tab:purple')
            ax[1].plot(spectrometer_position, residuals, label='Wavelength residuals', marker='o')
            ax[0].set_title('Triax Steps to Wavelength')
            ax[0].legend()
            ax[1].legend()

            print(f"R2: {r2:.4f}, RMSE: {rmse_val:.4f}, MAE: {mae_val:.4f}, Residual Std: {res_std:.4f}")

            plt.show()

        report_dict['triax_steps_to_wavelength'] = {'residuals': residuals_scaled,
                                                    'r2': r2,
                                                    'rmse': rmse_val,
                                                    'mae': mae_val,
                                                    'res_std': res_std}
        return steps_to_wavelength
    
    triax_steps = triax_steps_to_wavelength(spectrometer_position, wavelength_axis, show=True)
    calibrations['triax_steps_wl'] = triax_steps.tolist()
        
    new_data_array = np.column_stack((wavelength_axis, data_l1, data_l2, data_g1, data_g2))
    
    def wavelength_to_l1(new_data_array, show=True):
        '''Calibration for using laser wavelength to calculate L1 steps. Redundant if using fits from initial wavelength calibration.'''

        fit_coeff_wavelength_to_l1 = np.polyfit(new_data_array[:, 0], new_data_array[:, 1], 2)
        p_wavelength_to_l1 = np.poly1d(fit_coeff_wavelength_to_l1)

        if show is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(new_data_array[:, 0], new_data_array[:, 1], label='L1 Steps')
            ax[0].plot(new_data_array[:, 0], p_wavelength_to_l1(new_data_array[:, 0]), label='L1 Steps fit', color='tab:purple')
            residuals = new_data_array[:, 1] - p_wavelength_to_l1(new_data_array[:, 0])
            ax[1].plot(new_data_array[:, 0], residuals, label='L1 Steps residuals', marker='o')
            ax[0].set_title('Wavelength to L1 Steps')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        return fit_coeff_laser
    
    fit_coeff_laser = wavelength_to_l1(new_data_array)



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
    
    calibrations['laser'] = fit_coeff_laser.tolist()
    calibrations['grating'] = fit_coeff_grating.tolist()

    fig, ax = plt.subplots(3,1)
    wavelength_cal_laser = np.polyfit(wavelength_axis, data_l1, 2)
    wavelength_cal_grating = np.polyfit(wavelength_axis, data_g1, 1)
    p_wavelength_laser = np.poly1d(wavelength_cal_laser)
    p_wavelength_grating = np.poly1d(wavelength_cal_grating)
    ax[0].scatter(wavelength_axis, data_l1, label='Lambda L1')
    ax[0].plot(wavelength_axis, p_wavelength_laser(wavelength_axis), label='Lambda L1 fit', color='tab:purple')
    ax[1].scatter(wavelength_axis, data_g1, label='Lambda G1')
    ax[1].plot(wavelength_axis, p_wavelength_grating(wavelength_axis), label='Lambda G1 fit', color='tab:purple')
    
    res_1 = data_l1 - p_wavelength_laser(wavelength_axis)
    res_2 = data_g1 - p_wavelength_grating(wavelength_axis)
    ax[2].plot(wavelength_axis, res_1, label='Lambda L1 residuals', marker='o')
    ax[2].plot(wavelength_axis, res_2, label='Lambda G1 residuals', marker='o')

    ax[0].legend()
    ax[1].legend()
    ax[2].legend()

    if show is True:
        plt.show()
    
    calibrations['wavelength_laser'] = wavelength_cal_laser.tolist()
    calibrations['wavelength_grating'] = wavelength_cal_grating.tolist()

    steps_cal_laser = np.polyfit(data_l1, wavelength_axis, 2)
    steps_cal_grating = np.polyfit(data_g1, wavelength_axis, 1)
    p_steps_laser = np.poly1d(steps_cal_laser)
    p_steps_grating = np.poly1d(steps_cal_grating)

    fig, ax = plt.subplots(4,1)
    ax[0].scatter(data_l1, wavelength_axis, label='Lambda L1')
    ax[1].scatter(data_g1, wavelength_axis, label='Lambda G1')
    ax[0].plot(data_l1, p_steps_laser(data_l1), label='Lambda L1 fit', color='tab:purple')
    ax[1].plot(data_g1, p_steps_grating(data_g1), label='Lambda G1 fit', color='tab:purple')
    ax[0].set_title('back calibrate stepts to wavelength')
    residual_laser = wavelength_axis - p_steps_laser(data_l1)
    residual_grating = wavelength_axis - p_steps_grating(data_g1)
    ax[2].plot(data_l1, residual_laser, label='Lambda L1 residuals', marker='o')
    ax[3].plot(data_g1, residual_grating, label='Lambda G1 residuals', marker='o')
    # ax[0].set_title()
    ax[0].legend()
    ax[1].legend()
    ax[2].legend()
    ax[3].legend()
    plt.show()

    calibrations['steps_laser'] = steps_cal_laser.tolist()
    calibrations['steps_grating'] = steps_cal_grating.tolist()

    print(f'steps_laser fit: {steps_cal_laser}')
    print(f'steps_grating fit: {steps_cal_grating}')
    print(f'wavelength_laser fit: {wavelength_cal_laser}')
    print(f'wavelength_grating fit: {wavelength_cal_grating}')




    return calibrations

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
    calibrations = run_motor_calibration(headers, cal_data, calib_dict, wavelength_cal, show=True)
    # save calibration data as json

    with open(os.path.join(os.path.dirname(__file__), 'calibrations.json'), 'w') as f:
        json.dump(calibrations, f)



