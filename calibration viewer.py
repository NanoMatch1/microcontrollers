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

        self.initial_wavelength_cal = self.initial_wavelength_calibration(show=False)

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

        # wavelength_data = (np.array(data_set_1).astype(float), np.array(data_set_2).astype(float))
        wavelength_data = np.array(data_set_1).astype(float)
        return wavelength_data
    
    def load_eept_file(self, plot_rows=[0,1,4,5]):
        cal_data = np.array(["L1", "L2", "NIU", "NIU", "G1", "G2", "NIU", "NIU", "triax_steps", "pixels"])
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

        cal_data = {header: cal_data_array[:, idx] for idx, header in enumerate(headers)}

        return cal_data
    
    def load_aapt_file(self):
        cal_data = np.array(["wavelength", "L1", "L2", "NIU", "NIU", "G1", "G2", "NIU", "NIU"])
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

                # breakpoint()
                # breakpoint()
                cal_data = np.column_stack((cal_data, new_data))

        headers = cal_data.T[0, :]
        cal_data_array = cal_data.T[1:, :].astype(float)

        cal_data = {header: cal_data_array[:, idx] for idx, header in enumerate(headers)}

        return cal_data


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


        coeff_l1_to_wl = np.polyfit(l1_steps, wavelength, 2)
        p_wavelength = np.poly1d(coeff_l1_to_wl)

        y_pred2 = p_wavelength(l1_steps)
        residuals2 = wavelength - y_pred2
        residuals_scaled2 = (residuals2/wavelength) * 100

        # Fit quality metrics
        fit_metrics2 = self.calculate_fit_metrics(wavelength, y_pred2)

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

        # self.calibration_metrics['wl_to_l1'] = fit_metrics
        # self.calibrations['wl_to_l1'] = coeff_wl_to_l1.tolist()

        return {'wl_to_l1': (coeff_wl_to_l1, fit_metrics), 'l1_to_wl': (coeff_l1_to_wl, fit_metrics2)}

    def run_motor_calibration(self, cal_data, calib_dict, show=False, recalculate_l1=False):
        pass

    def calculate_triax_steps(steps_and_pixels: tuple, wavelength_axis, calib_dict):
        '''Perparatory calculation. Calculates the correct number of steps for each wavelength in the calibration data to be at pixel 50 on the spectrometer'''

        spectrometer_position = []

        spectrometer_steps, pixel_number = steps_and_pixels
        # spectrometer_steps = sorted_data[:, 8]
        # pixel_number = sorted_data[:, 9]

        for idx, steps in enumerate(spectrometer_steps):
            wavelength = wavelength_axis[idx]
            pixel = pixel_number[idx]
            wavelength_from_50 = calib_dict['nm_per_pixel']*(50-pixel)
            triax_steps_to_shift = wavelength_from_50/calib_dict['nm_per_triax_step']
            print(pixel, triax_steps_to_shift, steps, wavelength)
            triax_actual_steps = steps + (wavelength_from_50/calib_dict['nm_per_triax_step'])
            spectrometer_position.append(triax_actual_steps)

        return spectrometer_position



        def wavelength_to_triax(spectrometer_position, wavelength_axis, show=False):
            '''Calibration for using laser wavelength to calculate spectrometer position in TRIAX steps. '''
            
            triax_steps = np.polyfit(wavelength_axis, spectrometer_position, 2)
            p_triax_steps = np.poly1d(triax_steps)
            
            y_pred = p_triax_steps(wavelength_axis)
            residuals = spectrometer_position - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(spectrometer_position, y_pred)

            if show is True or self.showplots is True:
                fig, ax = plt.subplots(2, 1)
                ax[0].scatter(wavelength_axis, spectrometer_position, label='Triax Steps')
                ax[0].plot(wavelength_axis, y_pred, label=f'Triax Steps fit (R2={fit_metrics.r2:.8f})', color='tab:purple')
                ax[1].plot(wavelength_axis, residuals, label='Triax Steps residuals', marker='o')
                ax[0].set_title('Wavelength to Triax Steps')
                ax[0].legend()
                ax[1].legend()
                plt.show()

            return triax_steps, fit_metrics



        def triax_steps_to_wavelength(spectrometer_position, wavelength_axis, show=False):
            '''Reverse calibration for calculating laser wavelength from spectrometer position in TRIAX steps.'''

            steps_to_wavelength = np.polyfit(spectrometer_position, wavelength_axis, 2)
            p_steps_to_wavelength = np.poly1d(steps_to_wavelength)

            y_pred = p_steps_to_wavelength(spectrometer_position)
            residuals = wavelength_axis - y_pred
            residuals_scaled = (residuals/wavelength_axis) * 100

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(wavelength_axis, y_pred)

            if show is True or self.showplots is True:
                fig, ax = plt.subplots(2, 1)
                ax[0].scatter(spectrometer_position, wavelength_axis, label='Wavelength')
                ax[0].plot(spectrometer_position, y_pred, label=f'Wavelength fit (R2={fit_metrics.r2:.8f})', color='tab:purple')
                ax[1].plot(spectrometer_position, residuals, label='Wavelength residuals', marker='o')
                ax[0].set_title('Triax Steps to Wavelength')
                ax[0].legend()
                ax[1].legend()

                # print(f"R2: {r2:.4f}, RMSE: {rmse_val:.4f}, MAE: {mae_val:.4f}, Residual Std: {res_std:.4f}")

                plt.show()

            # report_dict['triax_steps_to_wavelength'] = {
            #     'residuals': residuals_scaled,
            #     'r2': r2,
            #     'rmse': rmse_val,
            #     'mae': mae_val,
            #     'res_std': res_std
            #     }
            return steps_to_wavelength, fit_metrics
        

        
        def wavelength_to_l1(new_data_array, show=False):
            '''Calibration for using laser wavelength to calculate L1 steps.'''

            l1_steps = new_data_array[:, 1]
            fit_coeff_wavelength_to_l1 = np.polyfit(self.wavelength_axis, l1_steps, 2)
            p_wavelength_to_l1 = np.poly1d(fit_coeff_wavelength_to_l1)

            y_pred = p_wavelength_to_l1(self.wavelength_axis)
            residuals = l1_steps - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(l1_steps, y_pred)

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

            return fit_coeff_wavelength_to_l1, fit_metrics
        


        def l1_to_wavelength(new_data_array, show=False):
            '''Reverse calibration for calculating laser wavelength from L1 steps.'''

            l1_steps = new_data_array[:, 1]
            fit_coeff_l1_to_wavelength = np.polyfit(l1_steps, self.wavelength_axis, 2)
            p_l1_to_wavelength = np.poly1d(fit_coeff_l1_to_wavelength)

            y_pred = p_l1_to_wavelength(l1_steps)
            residuals = self.wavelength_axis - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)

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

            return fit_coeff_l1_to_wavelength, fit_metrics



        def wavelength_to_l2(new_data_array, show=False):
            '''Calibration for using laser wavelength to calculate L2 steps.'''

            l2_steps = new_data_array[:, 2]
            fit_coeff_wavelength_to_l2 = np.polyfit(self.wavelength_axis, l2_steps, 2)
            p_wavelength_to_l2 = np.poly1d(fit_coeff_wavelength_to_l2)

            y_pred = p_wavelength_to_l2(self.wavelength_axis)
            residuals = l2_steps - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(l2_steps, y_pred)

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

            return fit_coeff_wavelength_to_l2, fit_metrics
        
        def l2_to_wavelength(new_data_array, show=False):
            '''Reverse calibration for calculating laser wavelength from L2 steps.'''

            l2_steps = new_data_array[:, 2]
            fit_coeff_l2_to_wavelength = np.polyfit(l2_steps, self.wavelength_axis, 2)
            p_l2_to_wavelength = np.poly1d(fit_coeff_l2_to_wavelength)

            y_pred = p_l2_to_wavelength(l2_steps)
            residuals = self.wavelength_axis - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)

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

            return fit_coeff_l2_to_wavelength, fit_metrics

        def wavelength_to_g1(new_data_array, show=False):
            '''Calibration for using laser wavelength to calculate G1 steps.'''

            g1_steps = new_data_array[:, 3]
            fit_coeff_wavelength_to_g1 = np.polyfit(self.wavelength_axis, g1_steps, 1)
            p_wavelength_to_g1 = np.poly1d(fit_coeff_wavelength_to_g1)

            y_pred = p_wavelength_to_g1(self.wavelength_axis)
            residuals = g1_steps - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(g1_steps, y_pred)

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

            return fit_coeff_wavelength_to_g1, fit_metrics
        
        def g1_to_wavelength(new_data_array, show=False):
            '''Reverse calibration for calculating laser wavelength from G1 steps.'''

            g1_steps = new_data_array[:, 3]
            fit_coeff_g1_to_wavelength = np.polyfit(g1_steps, self.wavelength_axis, 1)
            p_g1_to_wavelength = np.poly1d(fit_coeff_g1_to_wavelength)

            y_pred = p_g1_to_wavelength(g1_steps)
            residuals = self.wavelength_axis - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)

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

            return fit_coeff_g1_to_wavelength, fit_metrics
        
        def wavelength_to_g2(new_data_array, show=False, offset=0, flipdir=True):
            '''Calibration for using laser wavelength to calculate G2 steps.'''

            g2_steps = (new_data_array[:, 4]*-1)+offset
            fit_coeff_wavelength_to_g2 = np.polyfit(self.wavelength_axis, g2_steps, 1)
            p_wavelength_to_g2 = np.poly1d(fit_coeff_wavelength_to_g2)

            y_pred = p_wavelength_to_g2(self.wavelength_axis)
            residuals = g2_steps - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(g2_steps, y_pred)

            if show is True or self.showplots is True:
                fig, ax = plt.subplots(2, 1)
                ax[0].scatter(self.wavelength_axis, g2_steps, label='G2 Steps')
                ax[0].plot(self.wavelength_axis, p_wavelength_to_g2(self.wavelength_axis), label='G2 Steps fit', color='tab:purple')
                residuals = g2_steps - p_wavelength_to_g2(self.wavelength_axis)
                ax[1].plot(self.wavelength_axis, residuals, label='G2 Steps residuals', marker='o')
                ax[0].set_title('Wavelength to G2 Steps (+{})'.format(offset))
                ax[0].legend()
                ax[1].legend()
                plt.show()

            return fit_coeff_wavelength_to_g2, fit_metrics
        
        def g2_to_wavelength(new_data_array, show=False, offset=0):
            '''Reverse calibration for calculating laser wavelength from G2 steps.'''

            g2_steps = (new_data_array[:, 4]*-1)+offset
            fit_coeff_g2_to_wavelength = np.polyfit(g2_steps, self.wavelength_axis, 1)
            p_g2_to_wavelength = np.poly1d(fit_coeff_g2_to_wavelength)

            y_pred = p_g2_to_wavelength(g2_steps)
            residuals = self.wavelength_axis - y_pred

            # Fit quality metrics
            fit_metrics = self.calculate_fit_metrics(self.wavelength_axis, y_pred)

            if show is True or self.showplots is True:
                fig, ax = plt.subplots(2, 1)
                ax[0].scatter(g2_steps, self.wavelength_axis, label='Wavelength')
                ax[0].plot(g2_steps, p_g2_to_wavelength(g2_steps), label='Wavelength fit', color='tab:purple')
                residuals = self.wavelength_axis - p_g2_to_wavelength(g2_steps)
                ax[1].plot(g2_steps, residuals, label='Wavelength residuals', marker='o')
                ax[0].set_title('G2 Steps (+{}) to Wavelength'.format(offset))
                ax[0].legend()
                ax[1].legend()
                plt.show()

            return fit_coeff_g2_to_wavelength, fit_metrics
        
        calibrations = {}
        report_dict = {}

        

        # fig, ax = plt.subplots(3,1)

        sorted_data = cal_data[np.argsort(cal_data[:, 0])]
        # breakpoint()
        data_l1 = sorted_data[:, 0]
        data_l2 = sorted_data[:, 1]
        data_g1 = sorted_data[:, 4]
        data_g2 = sorted_data[:, 5]

        # recalculates wavelength to l1 calibration to trim the data to the appropriate size for the other calibrations
        # calculate new wavelength axis with data_l1

        p_l1_to_wl = np.poly1d(self.initial_wavelength_cal['l1_to_wl'][0])
        self.wavelength_axis = p_l1_to_wl(data_l1)
        print('New wavelength axis calculated: \n', self.wavelength_axis)
        # breakpoint()




        spectrometer_position = calculate_triax_steps(sorted_data, self.wavelength_axis, Calibration.calib_dict)
        # breakpoint()
        new_data_array = np.column_stack((self.wavelength_axis, data_l1, data_l2, data_g1, data_g2))

        triax_steps, fm1 = wavelength_to_triax(spectrometer_position, self.wavelength_axis, show=True)
        self.calibration_metrics['wl_to_triax_steps'] = fm1
        self.calibrations['wl_to_triax_steps'] = triax_steps.tolist()

        triax_steps, fm2 = triax_steps_to_wavelength(spectrometer_position, self.wavelength_axis, show=True)
        self.calibration_metrics['triax_steps_to_wl'] = fm2
        self.calibrations['triax_steps_to_wl'] = triax_steps.tolist()
            
        fit_coeff_wavelength_to_l1, fm3 = wavelength_to_l1(new_data_array)
        self.calibration_metrics['wl_to_l1'] = fm3
        self.calibrations['wl_to_l1'] = fit_coeff_wavelength_to_l1.tolist()

        fit_coeff_l1_to_wavelength, fm4 = l1_to_wavelength(new_data_array)
        self.calibration_metrics['l1_to_wl'] = fm4
        self.calibrations['l1_to_wl'] = fit_coeff_l1_to_wavelength.tolist()

        fit_coeff_wavelength_to_l2, fm5 = wavelength_to_l2(new_data_array)
        self.calibration_metrics['wl_to_l2'] = fm5
        self.calibrations['wl_to_l2'] = fit_coeff_wavelength_to_l2.tolist()

        fit_coeff_l2_to_wavelength, fm6 = l2_to_wavelength(new_data_array)
        self.calibration_metrics['l2_to_wl'] = fm6
        self.calibrations['l2_to_wl'] = fit_coeff_l2_to_wavelength.tolist()

        fit_coeff_wavelength_to_g1, fm7 = wavelength_to_g1(new_data_array)
        self.calibration_metrics['wl_to_g1'] = fm7
        self.calibrations['wl_to_g1'] = fit_coeff_wavelength_to_g1.tolist()

        fit_coeff_g1_to_wavelength, fm8 = g1_to_wavelength(new_data_array)
        self.calibration_metrics['g1_to_wl'] = fm8
        self.calibrations['g1_to_wl'] = fit_coeff_g1_to_wavelength.tolist()

        fit_coeff_wavelength_to_g2, fm9 = wavelength_to_g2(new_data_array)
        self.calibration_metrics['wl_to_g2'] = fm9
        self.calibrations['wl_to_g2'] = fit_coeff_wavelength_to_g2.tolist()

        fit_coeff_g2_to_wavelength, fm10 = g2_to_wavelength(new_data_array)
        self.calibration_metrics['g2_to_wl'] = fm10
        self.calibrations['g2_to_wl'] = fit_coeff_g2_to_wavelength.tolist()

        fit_coeff_wavelength_to_g2_add, fm11 = wavelength_to_g2(new_data_array, offset=-13069)
        self.calibration_metrics['wl_to_g2_add'] = fm11
        self.calibrations['wl_to_g2_add'] = fit_coeff_wavelength_to_g2_add.tolist()

        fit_coeff_g2_to_wavelength_add, fm12 = g2_to_wavelength(new_data_array, offset=-13069)
        self.calibration_metrics['g2_to_wl_add'] = fm12
        self.calibrations['g2_to_wl_add'] = fit_coeff_g2_to_wavelength_add.tolist()


        return self.calibrations

        # fit_coeff_laser = np.polyfit(data_l1, data_l2, 1)
        # fit_coeff_grating = np.polyfit(data_g1, data_g2, 1)
        # ax[0].scatter(data_l1, data_l2, label='L1 vs L2')
        # ax[1].scatter(data_g1, data_g2, label='G1 vs G2')

    
        # # fit a line to the data

        # # get fit parameters
        # p_laser = np.poly1d(fit_coeff_laser)
        # p_grating = np.poly1d(fit_coeff_grating)

        # ax[0].plot(data_l1, p_laser(data_l1), label='L1 vs L2 fit', color='tab:purple')
        # ax[1].plot(data_g1, p_grating(data_g1), label='G1 vs G2 fit', color='tab:purple')

        # # plot residuals
        # residuals_l = data_l2 - p_laser(data_l1)
        # residuals_g = data_g2 - p_grating(data_g1)
        # ax[2].plot(data_l1, residuals_l, label='L1 vs L2 residuals', marker='o')
        # ax[2].plot(data_l1, residuals_g, label='G1 vs G2 residuals', marker='o')

        # ax[0].legend()
        # ax[1].legend()
        # ax[2].legend()
        
        # if show is True:
        #     plt.show()

        

        # print(f'l1xl2 fit: {fit_coeff_laser}')
        # print(f'g1xg2 fit: {fit_coeff_grating}')
        
        # calibrations['laser'] = fit_coeff_laser.tolist()
        # calibrations['grating'] = fit_coeff_grating.tolist()

        # fig, ax = plt.subplots(3,1)
        # wavelength_cal_laser = np.polyfit(wavelength_axis, data_l1, 2)
        # wavelength_cal_grating = np.polyfit(wavelength_axis, data_g1, 1)
        # p_wavelength_laser = np.poly1d(wavelength_cal_laser)
        # p_wavelength_grating = np.poly1d(wavelength_cal_grating)
        # ax[0].scatter(wavelength_axis, data_l1, label='Lambda L1')
        # ax[0].plot(wavelength_axis, p_wavelength_laser(wavelength_axis), label='Lambda L1 fit', color='tab:purple')
        # ax[1].scatter(wavelength_axis, data_g1, label='Lambda G1')
        # ax[1].plot(wavelength_axis, p_wavelength_grating(wavelength_axis), label='Lambda G1 fit', color='tab:purple')
        
        # res_1 = data_l1 - p_wavelength_laser(wavelength_axis)
        # res_2 = data_g1 - p_wavelength_grating(wavelength_axis)
        # ax[2].plot(wavelength_axis, res_1, label='Lambda L1 residuals', marker='o')
        # ax[2].plot(wavelength_axis, res_2, label='Lambda G1 residuals', marker='o')

        # ax[0].legend()
        # ax[1].legend()
        # ax[2].legend()

        # if show is True:
        #     plt.show()
        
        # calibrations['wavelength_laser'] = wavelength_cal_laser.tolist()
        # calibrations['wavelength_grating'] = wavelength_cal_grating.tolist()

        # steps_cal_laser = np.polyfit(data_l1, wavelength_axis, 2)
        # steps_cal_grating = np.polyfit(data_g1, wavelength_axis, 1)
        # p_steps_laser = np.poly1d(steps_cal_laser)
        # p_steps_grating = np.poly1d(steps_cal_grating)

        # fig, ax = plt.subplots(4,1)
        # ax[0].scatter(data_l1, wavelength_axis, label='Lambda L1')
        # ax[1].scatter(data_g1, wavelength_axis, label='Lambda G1')
        # ax[0].plot(data_l1, p_steps_laser(data_l1), label='Lambda L1 fit', color='tab:purple')
        # ax[1].plot(data_g1, p_steps_grating(data_g1), label='Lambda G1 fit', color='tab:purple')
        # ax[0].set_title('back calibrate stepts to wavelength')
        # residual_laser = wavelength_axis - p_steps_laser(data_l1)
        # residual_grating = wavelength_axis - p_steps_grating(data_g1)
        # ax[2].plot(data_l1, residual_laser, label='Lambda L1 residuals', marker='o')
        # ax[3].plot(data_g1, residual_grating, label='Lambda G1 residuals', marker='o')
        # # ax[0].set_title()
        # ax[0].legend()
        # ax[1].legend()
        # ax[2].legend()
        # ax[3].legend()
        # plt.show()

        # calibrations['steps_laser'] = steps_cal_laser.tolist()
        # calibrations['steps_grating'] = steps_cal_grating.tolist()

        # print(f'steps_laser fit: {steps_cal_laser}')
        # print(f'steps_grating fit: {steps_cal_grating}')
        # print(f'wavelength_laser fit: {wavelength_cal_laser}')
        # print(f'wavelength_grating fit: {wavelength_cal_grating}')

        # residuals
        
if __name__ == '__main__':
    # wavelength_cal = wavelength_calibration(laser_calibration, show=False)

    calibration = Calibration(showplots=False)
    # calibration.load_aapt_file()
    # breakpoint()
    cal_data = calibration.load_eept_file()
    breakpoint()
    calibration.calculate_triax_steps()
    breakpoint()
    calibration.run_motor_calibration(Calibration.calib_dict, cal_data, show=False, recalculate_l1=False)
    
    # return a solution for a given value of x, fed to the calibration function
    # x = 0.5
    # y = p(x)
    # give it wavelength, get steps
    # steps_from_nm = np.poly1d(wavelength_cal[0])
    # sol = steps_from_nm(802.5) # 17.219 steps
    # print(sol)
    # nm_from_steps = np.poly1d(wavelength_cal[1])
    # sol = nm_from_steps(227) # 799.1516 nm
    # sol = nm_from_steps(627) # 792.77096 nm # delta = 6.38064 nm
    # print(sol)


    # breakpoint()
    # headers, cal_data = process_eept(eept_file)
    # calibrations = run_motor_calibration(headers, cal_data, calib_dict, wavelength_cal, show=True)
    # save calibration data as json

    with open(os.path.join(os.path.dirname(__file__), 'calibrations.json'), 'w') as f:
        json.dump(calibration.calibrations, f)

    print("Calibration complete: Successfully saved calibration data to 'calibrations.json' file.")



