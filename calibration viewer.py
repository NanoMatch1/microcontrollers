import csv
import json
from dataclasses import dataclass


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



laser_calibration = {}

def review_report():
    with open(os.path.join(os.path.dirname(__file__), 'calibration_report.json'), 'r') as f:
        data = json.load(f)
        for key, value in data.items():
            print(key)
            for k, v in value.items():
                print(k)
                print(v)
                # print('\n')

def r_squared(y_true, y_pred):
    '''Calculate R^2 (coefficient of determination) for a regression model.'''
    ss_res = np.sum((y_true - y_pred) ** 2)  # Residual sum of squares
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)  # Total sum of squares
    return 1 - (ss_res / ss_tot)

def rmse(y_true, y_pred):
    '''Calculate the root mean squared error for a regression model.'''
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def mae(y_true, y_pred):
    '''Calculate the mean absolute error for a regression model.'''
    return np.mean(np.abs(y_true - y_pred))

def residual_std(residuals):
    '''Calculate the standard deviation of residuals for a regression model.'''
    return np.std(residuals)

def adjusted_r_squared(y_true, y_pred, p):
    '''Calculate the adjusted R^2 (coefficient of determination) for a regression model.'''
    n = len(y_true)
    r2 = r_squared(y_true, y_pred)
    return 1 - (1 - r2) * (n - 1) / (n - p - 1)

@dataclass
class FitMetrics:
    '''Dataclass for fit quality metrics.'''
    r2: int
    rmse: int
    mae: int
    res_std: int

class Calibration:

    calib_dict = {
    'pixels_per_laser_step': -194/200,
    'nm_per_laser_step': -0.01635,
    'nm_per_pixel': -0.01635/-0.97, #0.0168557

    # 'nm_per_pixel': -6.32/400, # retrieved from recent calibration sweep
    # nm_per_step = 0
    'triax_steps': 375000,
    'nm_per_triax_step': -0.002062
    }

    def __init__(self, showplots=False):
        # self.data = data
        self.dataDir = os.path.join(os.path.dirname(__file__), 'laser_calibration')
        self.files = [f for f in os.listdir(self.dataDir) if f.endswith('.txt')]
        self.eept_file = os.path.join(os.path.dirname(__file__), 'eept.txt')
        self.aapt_file = os.path.join(os.path.dirname(__file__), 'aapt.txt')
        self.showplots = showplots
        self.calibration_metrics = {}
        self.calibrations = {}
        self.report_dict = {'initial': {}, 'subtractive': {}, 'additive': {}}

    def load_calibration_file(self):
        file = self.files[0]

        with open(os.path.join(self.dataDir, file), 'r') as f:
            lines = f.readlines()
            data_set_1 = []
            data_set_2 = []
            for line in lines:
                if line.startswith('#'):
                    continue
                cols = line.split(',')
                data_set_1.append([cols[0], cols[3]])
                # data_set_2.append([float(cols[3]), float(cols[0])])

        wavelength_data = np.array(data_set_1).astype(float)
        return wavelength_data
    
    def load_eept_file(self, plot_rows=[0,1,4,5]):
        cal_data = np.array(["l1", "l2", "NIU", "NIU", "g1", "g2", "NIU", "NIU", "triax_steps", "pixels"])
        with open(self.eept_file, 'r') as f:
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
        cal_data_array = cal_data.T[1:, :].astype(float)

        # sort the data by steps on l1 (/propto wavelength)
        sorted_data = cal_data_array[np.argsort(cal_data_array[:, 0])]

        cal_data = {header: sorted_data[:, idx] for idx, header in enumerate(headers)}

        return cal_data, sorted_data
    
    def load_aapt_file(self):
        cal_data = np.array(["wavelength", "l1", "l2", "NIU", "NIU", "g1", "g2", "NIU", "NIU"])
        with open(self.aapt_file, 'r') as f:
            lines = f.readlines()

            for line in lines:
                data = []
                if line.startswith('#'):
                    continue
                line = line.strip('\n')
                if len(line) == 0:
                    continue
                try:
                    wavelength, set_avo, set_gary, set_triax = line.split(':')
                except Exception as e:
                    print(e)
                    print("check data file aapt.txt")
                    continue
        
                set_avo = set_avo.strip('[]')
                set_gary = set_gary.strip('[]')

                set_avo = set_avo.split(',')
                set_gary = set_gary.split(',')
                set_triax = set_triax.split(',')

                data.extend([wavelength, *set_avo, *set_gary])
                new_data = []
                for x in data:
                    value = float(x.strip("' XYZA"))
                    new_data.append(value)


                cal_data = np.column_stack((cal_data, new_data))

        headers = cal_data.T[0, :]
        cal_data_array = cal_data.T[1:, :].astype(float)

        sorted_data = cal_data_array[np.argsort(cal_data_array[:, 0])]

        cal_data = {header: sorted_data[:, idx] for idx, header in enumerate(headers)}

        self.wavelength_axis = cal_data['wavelength']

        return cal_data, sorted_data


    def calculate_fit_metrics(self, actual, model):
        # Fit quality metrics
        r2 = r_squared(actual, model)
        rmse_val = rmse(actual, model)
        mae_val = mae(actual, model)
        residuals = actual - model
        res_std = residual_std(residuals)

        return FitMetrics(r2, rmse_val, mae_val, res_std)

    def initial_wavelength_calibration(self, show=True):

        fig, ax = plt.subplots(2,2)

        wavelength_data = self.load_calibration_file()
        wavelength, l1_steps = wavelength_data[:, 0], wavelength_data[:, 1]

        coeff_wl_to_l1 = np.polyfit(wavelength, l1_steps, 2)
        p_l1_steps = np.poly1d(coeff_wl_to_l1)

        y_pred = p_l1_steps(wavelength)
        residuals = l1_steps - y_pred
        residuals_scaled = (residuals/abs(l1_steps[0]-l1_steps[1])) * 100

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(l1_steps, y_pred)
        self.report_dict['initial']['wl_to_l1'] = (fit_metrics, coeff_wl_to_l1.tolist())

        coeff_l1_to_wl = np.polyfit(l1_steps, wavelength, 2)
        p_wavelength = np.poly1d(coeff_l1_to_wl)

        y_pred2 = p_wavelength(l1_steps)
        residuals2 = wavelength - y_pred2
        residuals_scaled2 = (residuals2/wavelength) * 100

        # Fit quality metrics
        fit_metrics2 = self.calculate_fit_metrics(wavelength, y_pred2)
        self.report_dict['initial']['l1_to_wl'] = (fit_metrics2, coeff_l1_to_wl.tolist())

        if show is True or self.showplots is True:
            ax[0, 0].scatter(wavelength, l1_steps, label='l1 steps')
            ax[0, 0].plot(wavelength, p_l1_steps(wavelength), label='wl to l1 fit', color='tab:purple')
            ax[1, 0].plot(wavelength, residuals_scaled, label='residuals', marker='o')
            ax[1, 0].set_ylabel('% of $\Delta_{steps}$')
            ax[1, 0].set_xlabel('Wavelength (nm)')
            ax[0, 0].set_title('Wavelength to L1 Steps')
            ax[0, 0].legend()
            ax[1, 0].legend()

            ax[0, 1].scatter(l1_steps, wavelength, label='wavelength')
            ax[0, 1].plot(l1_steps, p_wavelength(l1_steps), label='l1 to wl fit', color='tab:purple')
            ax[1, 1].plot(l1_steps, residuals_scaled2, label='residuals', marker='o')
            ax[1, 1].set_ylabel('% of $\Delta_{\lambda}$')
            ax[1, 1].set_xlabel('L1 Steps')
            ax[0, 1].set_title('L1 Steps to Wavelength')
            ax[0, 1].legend()
            ax[1, 1].legend()


            plt.show()

        return {'wl_to_l1': (coeff_wl_to_l1, fit_metrics), 'l1_to_wl': (coeff_l1_to_wl, fit_metrics2)}
    
    def save_report(self):
        # unpack report_dict into dict for json serialization
        newDict = {x: y for x, y in self.report_dict.items()}
        for mode, data in self.report_dict.items():
            for key, value in data.items():
                newDict[mode][key] = (value[0].__dict__, value[1])

        with open(os.path.join(os.path.dirname(__file__), 'calibration_report.json'), 'w') as f:
            json.dump(newDict, f)
    
    def build_wavelength_axis(self, initial_wavelength_cal, l1_data):
        p_l1_to_wl = np.poly1d(initial_wavelength_cal['l1_to_wl'][0])
        self.wavelength_axis = p_l1_to_wl(l1_data)
        print('New wavelength axis calculated: \n', self.wavelength_axis)
        return self.wavelength_axis

    def save_triax_calibrations(self):
        triax_cals = {key: value for key, value in self.calibrations.items() if 'triax' in key}

        with open(os.path.join(os.path.dirname(__file__), 'TRIAX_calibration.json'), 'w') as f:
            json.dump(triax_cals, f)

        print("Successfully saved TRIAX calibration data to 'TRIAX_calibration.json' file.")

    def save_all_calibrations(self):
        with open(os.path.join(os.path.dirname(__file__), 'calibrations.json'), 'w') as f:
            json.dump(calibration.calibrations, f)

        print("Calibration complete: Successfully saved calibration data to 'calibrations.json' file.")

    def calculate_triax_steps(self, steps_and_pixels: tuple, wavelength_axis=None, calib_dict=None):
        '''Perparatory calculation. Calculates the correct number of steps for each wavelength in the calibration data to be at pixel 50 on the spectrometer'''

        if wavelength_axis is None:
            wavelength_axis = self.wavelength_axis

        if calib_dict is None:
            calib_dict = Calibration.calib_dict

        spectrometer_position = []

        spectrometer_steps, pixel_number = steps_and_pixels

        for idx, steps in enumerate(spectrometer_steps):
            wavelength = wavelength_axis[idx]
            pixel = pixel_number[idx]
            wavelength_from_50 = calib_dict['nm_per_pixel']*(50-pixel)
            triax_steps_to_shift = wavelength_from_50/calib_dict['nm_per_triax_step']
            print(pixel, triax_steps_to_shift, steps, wavelength)
            triax_actual_steps = steps + (wavelength_from_50/calib_dict['nm_per_triax_step'])
            spectrometer_position.append(triax_actual_steps)

        self.spectrometer_position = spectrometer_position

        return spectrometer_position



    def wavelength_to_triax(self, spectrometer_position=None, wavelength_axis=None, show=False):
        '''Calibration for using laser wavelength to calculate spectrometer position in TRIAX steps. '''
        
        if spectrometer_position is None:
            spectrometer_position = self.spectrometer_position

        if wavelength_axis is None:
            wavelength_axis = self.wavelength_axis

        triax_steps = np.polyfit(wavelength_axis, spectrometer_position, 2)
        p_triax_steps = np.poly1d(triax_steps)
        
        y_pred = p_triax_steps(wavelength_axis)
        residuals = spectrometer_position - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(spectrometer_position, y_pred)
        self.report_dict['initial']['wl_to_triax_steps'] = (fit_metrics, triax_steps.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(wavelength_axis, spectrometer_position, label='Triax Steps')
            ax[0].plot(wavelength_axis, y_pred, label=f'Triax Steps fit (R2={fit_metrics.r2:.8f})', color='tab:purple')
            ax[1].plot(wavelength_axis, residuals, label='Triax Steps residuals', marker='o')
            ax[0].set_title('Wavelength to Triax Steps')
            ax[0].legend()
            ax[1].legend()
            plt.show()


        self.calibration_metrics['wl_to_triax_steps'] = fit_metrics
        self.calibrations['wl_to_triax_steps'] = triax_steps.tolist()

        return triax_steps, fit_metrics



    def triax_steps_to_wavelength(self, spectrometer_position=None, wavelength_axis=None, show=False):
        '''Reverse calibration for calculating laser wavelength from spectrometer position in TRIAX steps.'''

        if spectrometer_position is None:
            spectrometer_position = self.spectrometer_position
        
        if wavelength_axis is None:
            wavelength_axis = self.wavelength_axis

        steps_to_wavelength = np.polyfit(spectrometer_position, wavelength_axis, 2)
        p_steps_to_wavelength = np.poly1d(steps_to_wavelength)

        y_pred = p_steps_to_wavelength(spectrometer_position)
        residuals = wavelength_axis - y_pred
        residuals_scaled = (residuals/wavelength_axis) * 100

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(wavelength_axis, y_pred)
        self.report_dict['initial']['triax_steps_to_wl'] = (fit_metrics, steps_to_wavelength.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(spectrometer_position, wavelength_axis, label='Wavelength')
            ax[0].plot(spectrometer_position, y_pred, label=f'Wavelength fit (R2={fit_metrics.r2:.8f})', color='tab:purple')
            ax[1].plot(spectrometer_position, residuals, label='Wavelength residuals', marker='o')
            ax[0].set_title('Triax Steps to Wavelength')
            ax[0].legend()
            ax[1].legend()

            plt.show()

        self.calibration_metrics['triax_steps_to_wl'] = fit_metrics
        self.calibrations['triax_steps_to_wl'] = steps_to_wavelength.tolist()

        return steps_to_wavelength, fit_metrics
        

        
    def wavelength_to_l1(self, l1_steps, poly_order=2, mode=None, show=False):
        '''Calibration for using laser wavelength to calculate L1 steps.'''

        if mode is None:
            assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'

        fit_coeff_wavelength_to_l1 = np.polyfit(self.wavelength_axis, l1_steps, poly_order)
        p_wavelength_to_l1 = np.poly1d(fit_coeff_wavelength_to_l1)

        y_pred = p_wavelength_to_l1(self.wavelength_axis)
        residuals = l1_steps - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(l1_steps, y_pred)
        self.report_dict[mode]['wl_to_l1'] = (fit_metrics, fit_coeff_wavelength_to_l1.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(self.wavelength_axis, l1_steps, label='L1 Steps')
            ax[0].plot(self.wavelength_axis, p_wavelength_to_l1(self.wavelength_axis), label='L1 Steps fit', color='tab:purple')
            residuals = l1_steps - p_wavelength_to_l1(self.wavelength_axis)
            ax[1].plot(self.wavelength_axis, residuals, label='L1 Steps residuals', marker='o')
            ax[0].set_title('Wavelength to L1 Steps')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['wl_to_l1'] = fit_metrics
        self.calibrations['wl_to_l1'] = fit_coeff_wavelength_to_l1.tolist()

        return fit_coeff_wavelength_to_l1, fit_metrics
        


    def l1_to_wavelength(self, l1_steps, poly_order=2, mode=None, show=False):
        '''Reverse calibration for calculating laser wavelength from L1 steps.'''

        if mode is None:
            assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'

        fit_coeff_l1_to_wavelength = np.polyfit(l1_steps, self.wavelength_axis, poly_order)
        p_l1_to_wavelength = np.poly1d(fit_coeff_l1_to_wavelength)

        y_pred = p_l1_to_wavelength(l1_steps)
        residuals = self.wavelength_axis - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)
        self.report_dict[mode]['l1_to_wl'] = (fit_metrics, fit_coeff_l1_to_wavelength.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(l1_steps, self.wavelength_axis, label='Wavelength')
            ax[0].plot(l1_steps, p_l1_to_wavelength(l1_steps), label='Wavelength fit', color='tab:purple')
            residuals = self.wavelength_axis - p_l1_to_wavelength(l1_steps)
            ax[1].plot(l1_steps, residuals, label='Wavelength residuals', marker='o')
            ax[0].set_title('L1 Steps to Wavelength')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['l1_to_wl'] = fit_metrics
        self.calibrations['l1_to_wl'] = fit_coeff_l1_to_wavelength.tolist()

        return fit_coeff_l1_to_wavelength, fit_metrics



    def wavelength_to_l2(self, l2_steps, poly_order=2, mode=None, show=False):
        '''Calibration for using laser wavelength to calculate L2 steps.'''

        assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'

        fit_coeff_wavelength_to_l2 = np.polyfit(self.wavelength_axis, l2_steps, poly_order)
        p_wavelength_to_l2 = np.poly1d(fit_coeff_wavelength_to_l2)

        y_pred = p_wavelength_to_l2(self.wavelength_axis)
        residuals = l2_steps - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(l2_steps, y_pred)
        self.report_dict[mode]['wl_to_l2'] = (fit_metrics, fit_coeff_wavelength_to_l2.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(self.wavelength_axis, l2_steps, label='L2 Steps')
            ax[0].plot(self.wavelength_axis, p_wavelength_to_l2(self.wavelength_axis), label='L2 Steps fit', color='tab:purple')
            residuals = l2_steps - p_wavelength_to_l2(self.wavelength_axis)
            ax[1].plot(self.wavelength_axis, residuals, label='L2 Steps residuals', marker='o')
            ax[0].set_title('Wavelength to L2 Steps')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['wl_to_l2'] = fit_metrics
        self.calibrations['wl_to_l2'] = fit_coeff_wavelength_to_l2.tolist()

        return fit_coeff_wavelength_to_l2, fit_metrics
        
    def l2_to_wavelength(self, l2_steps, poly_order=2, mode=None, show=False):
        '''Reverse calibration for calculating laser wavelength from L2 steps.'''

        assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'

        fit_coeff_l2_to_wavelength = np.polyfit(l2_steps, self.wavelength_axis, poly_order)
        p_l2_to_wavelength = np.poly1d(fit_coeff_l2_to_wavelength)

        y_pred = p_l2_to_wavelength(l2_steps)
        residuals = self.wavelength_axis - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)
        self.report_dict[mode]['l2_to_wl'] = (fit_metrics, fit_coeff_l2_to_wavelength.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(l2_steps, self.wavelength_axis, label='Wavelength')
            ax[0].plot(l2_steps, p_l2_to_wavelength(l2_steps), label='Wavelength fit', color='tab:purple')
            residuals = self.wavelength_axis - p_l2_to_wavelength(l2_steps)
            ax[1].plot(l2_steps, residuals, label='Wavelength residuals', marker='o')
            ax[0].set_title('L2 Steps to Wavelength')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['l2_to_wl'] = fit_metrics
        self.calibrations['l2_to_wl'] = fit_coeff_l2_to_wavelength.tolist()

        return fit_coeff_l2_to_wavelength, fit_metrics

    def wavelength_to_g1(self, g1_steps, poly_order=2, mode=None, show=False):
        '''Calibration for using laser wavelength to calculate G1 steps.'''

        assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'

        fit_coeff_wavelength_to_g1 = np.polyfit(self.wavelength_axis, g1_steps, poly_order)
        p_wavelength_to_g1 = np.poly1d(fit_coeff_wavelength_to_g1)

        y_pred = p_wavelength_to_g1(self.wavelength_axis)
        residuals = g1_steps - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(g1_steps, y_pred)
        self.report_dict[mode]['wl_to_g1'] = (fit_metrics, fit_coeff_wavelength_to_g1.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(self.wavelength_axis, g1_steps, label='G1 Steps')
            ax[0].plot(self.wavelength_axis, p_wavelength_to_g1(self.wavelength_axis), label='G1 Steps fit', color='tab:purple')
            residuals = g1_steps - p_wavelength_to_g1(self.wavelength_axis)
            ax[1].plot(self.wavelength_axis, residuals, label='G1 Steps residuals', marker='o')
            ax[0].set_title('Wavelength to G1 Steps')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['wl_to_g1'] = fit_metrics
        self.calibrations['wl_to_g1'] = fit_coeff_wavelength_to_g1.tolist()

        return fit_coeff_wavelength_to_g1, fit_metrics
        
    def g1_to_wavelength(self, g1_steps, poly_order=2, mode=None, show=False):
        '''Reverse calibration for calculating laser wavelength from G1 steps.'''

        assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'

        fit_coeff_g1_to_wavelength = np.polyfit(g1_steps, self.wavelength_axis, poly_order)
        p_g1_to_wavelength = np.poly1d(fit_coeff_g1_to_wavelength)

        y_pred = p_g1_to_wavelength(g1_steps)
        residuals = self.wavelength_axis - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)
        self.report_dict[mode]['g1_to_wl'] = (fit_metrics, fit_coeff_g1_to_wavelength.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(g1_steps, self.wavelength_axis, label='Wavelength')
            ax[0].plot(g1_steps, p_g1_to_wavelength(g1_steps), label='Wavelength fit', color='tab:purple')
            residuals = self.wavelength_axis - p_g1_to_wavelength(g1_steps)
            ax[1].plot(g1_steps, residuals, label='Wavelength residuals', marker='o')
            ax[0].set_title('G1 Steps to Wavelength')
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['g1_to_wl'] = fit_metrics
        self.calibrations['g1_to_wl'] = fit_coeff_g1_to_wavelength.tolist()
        
        return fit_coeff_g1_to_wavelength, fit_metrics
        
    def wavelength_to_g2(self, g2_steps, poly_order=2, mode=None, show=False):
        '''Calibration for using laser wavelength to calculate G2 steps.'''

        assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'
        
        fit_coeff_wavelength_to_g2 = np.polyfit(self.wavelength_axis, g2_steps, poly_order)
        p_wavelength_to_g2 = np.poly1d(fit_coeff_wavelength_to_g2)

        y_pred = p_wavelength_to_g2(self.wavelength_axis)
        residuals = g2_steps - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(g2_steps, y_pred)
        self.report_dict[mode]['wl_to_g2'] = (fit_metrics, fit_coeff_wavelength_to_g2.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(self.wavelength_axis, g2_steps, label='G2 Steps')
            ax[0].plot(self.wavelength_axis, p_wavelength_to_g2(self.wavelength_axis), label='G2 Steps fit', color='tab:purple')
            residuals = g2_steps - p_wavelength_to_g2(self.wavelength_axis)
            ax[1].plot(self.wavelength_axis, residuals, label='G2 Steps residuals', marker='o')
            ax[0].set_title('Wavelength to G2 Steps {}'.format(mode))
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['wl_to_g2_{}'.format(mode)] = fit_metrics
        self.calibrations['wl_to_g2_{}'.format(mode)] = fit_coeff_wavelength_to_g2.tolist()

        return fit_coeff_wavelength_to_g2, fit_metrics
    
    def g2_to_wavelength(self, g2_steps, poly_order=2, mode=None, show=False):
        '''Reverse calibration for calculating laser wavelength from G2 steps.'''

        assert mode in ['subtractive', 'additive'], 'Invalid mode. Must be either "subtractive" or "additive".'

        fit_coeff_g2_to_wavelength = np.polyfit(g2_steps, self.wavelength_axis, poly_order)
        p_g2_to_wavelength = np.poly1d(fit_coeff_g2_to_wavelength)

        y_pred = p_g2_to_wavelength(g2_steps)
        residuals = self.wavelength_axis - y_pred

        # Fit quality metrics
        fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)
        self.report_dict[mode]['g2_to_wl'] = (fit_metrics, fit_coeff_g2_to_wavelength.tolist())

        if show is True or self.showplots is True:
            fig, ax = plt.subplots(2, 1)
            ax[0].scatter(g2_steps, self.wavelength_axis, label='Wavelength')
            ax[0].plot(g2_steps, p_g2_to_wavelength(g2_steps), label='Wavelength fit', color='tab:purple')
            residuals = self.wavelength_axis - p_g2_to_wavelength(g2_steps)
            ax[1].plot(g2_steps, residuals, label='Wavelength residuals', marker='o')
            ax[0].set_title('G2 Steps to Wavelength {}'.format(mode))
            ax[0].legend()
            ax[1].legend()
            plt.show()

        self.calibration_metrics['g2_to_wl_{}'.format(mode)] = fit_metrics
        self.calibrations['g2_to_wl_{}'.format(mode)] = fit_coeff_g2_to_wavelength.tolist()

        return fit_coeff_g2_to_wavelength, fit_metrics
        
if __name__ == '__main__':
    def initialise(**kwargs):
    # initialise calibration object
        calibration = Calibration(**kwargs)
        # initial wavelength calibration
        initial_wavelength_cal = calibration.initial_wavelength_calibration(show=False)
        # load eept calibration file
        cal_data, cal_data_array = calibration.load_eept_file()
        print(cal_data.keys())

        # build wavelength axis
        calibration.build_wavelength_axis(initial_wavelength_cal, cal_data['l1'])
        
        # load aapt calibration file, if necessary
        # calibration.load_aapt_file()

        # calculate spectrometer position from triax steps and position
        spectrometer_position = calibration.calculate_triax_steps((cal_data['triax_steps'], cal_data['pixels']), calibration.wavelength_axis)

        print('Initialisation complete - spectrometer position calculated.')

        return calibration, cal_data




    def triax_calibrations(calibration, cal_data):
        calibration.wavelength_to_triax()
        calibration.triax_steps_to_wavelength(cal_data['l1'])
    
    def subtractive_calibrations(calibration, cal_data):
        # cal_data, cal_data_array = calibration.load_eept_file()
        calibration.wavelength_to_l1(cal_data['l1'], mode='subtractive')
        calibration.l1_to_wavelength(cal_data['l1'], mode='subtractive')
        calibration.wavelength_to_l2(cal_data['l2'], mode='subtractive')
        calibration.l2_to_wavelength(cal_data['l2'], mode='subtractive')
        calibration.wavelength_to_g1(cal_data['g1'], mode='subtractive')
        calibration.g1_to_wavelength(cal_data['g1'], mode='subtractive')
        calibration.wavelength_to_g2(cal_data['g2'], mode='subtractive')
        calibration.g2_to_wavelength(cal_data['g2'], mode='subtractive')

    # FEAT Make additive calibrations

    def additive_calibrations(calibration, cal_data, repeat=True):
        cal_data, cal_data_array = calibration.load_aapt_file()
        
        if repeat is True:
            # calibrate L1
            l1_steps = cal_data['l1']
            calibration.wavelength_to_l1(l1_steps, mode='additive')
            calibration.l1_to_wavelength(l1_steps, mode='additive')

            # calibrate L2
            l2_steps = cal_data['l2']
            calibration.wavelength_to_l2(l2_steps, mode='additive')
            calibration.l2_to_wavelength(l2_steps, mode='additive')

            # calibrate G1
            g1_steps = cal_data['g1']
            calibration.wavelength_to_g1(g1_steps, mode='additive')
            calibration.g1_to_wavelength(g1_steps, mode='additive')

        # calibrate G2
        g2_steps = cal_data['g2']
        calibration.wavelength_to_g2(g2_steps, mode='additive')
        calibration.g2_to_wavelength(g2_steps, mode='additive')


    calibration, cal_data = initialise(showplots=False)
    triax_calibrations(calibration, cal_data)
    subtractive_calibrations(calibration, cal_data)
    additive_calibrations(calibration, cal_data)
    # TRIAX cal is absolute - only needs to be saved once
    # calibration.save_triax_calibrations()
    calibration.save_all_calibrations()
    calibration.save_report()
    # review_report()
    # print(calibration.calibrations)

