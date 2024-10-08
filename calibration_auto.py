import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis-spectroscopy','analysis_spectroscopy'))

# basename = os.path.dirname(os.path.dirname(__file__))
# sys.path.append(os.path.join(basename, 'analysis-spectroscopy'))
from analysis_spectroscopy import dataset_analysis as asp

def sort_by_key(value):
    return int(value.split('_')[1])

def get_latest_calibration_file(dataDir):
    fileList = [file for file in os.listdir(os.path.join(os.path.dirname(__file__), 'autocalibration')) if file.endswith('.json')]
    sorted_files = sorted(fileList, key=lambda x: int(x.split('_')[1]))
    return sorted_files[-1]

# note: only works on one file at a time


class Peaks:

    def __init__(self, peak_type, position, amplitude, fwhm, eta=None):
        self.peak_type = peak_type
        self.pos = position
        self.amp = amplitude
        self.fwhm = fwhm
        self.eta = eta

    def __repr__(self):
        return f'Peak Object(pos={round(self.pos, 2)}, amp={round(self.amp, 2)}, fwhm={round(self.fwhm, 2)})'



def peakfit_autocal(scriptDir, dataDir):
    working_calibration_file = get_latest_calibration_file(dataDir)
    dataSet = asp.DataSet(dataDir, fileList=[working_calibration_file])

    fileObj = dataSet.dataDict.get(working_calibration_file)
    dataSet.dataDict = fileObj.data

    for cal_obj in dataSet.dataDict.values():
        cal_obj._invert_data()

    dataSet.minimise_all()
    # dataSet.baseline_all(show=False, lam=100, p=0.01)

    peakfitting_info = {
        'peak_list': [],
        'peak_type': 'voigt_pseudo',
        'peak_sign': 'positive',
        'threshold': 0.05, # percentage of max intensity
        'peak_detect': 'all',
        'copy_peaks': False,
    }
    dataSet._peakfit(peakfitting_info=peakfitting_info)
    dataSet.save_database(tagList='', seriesName='autocal')

def generate_autocal(scriptDir, dataDir):
    key_index = {
        'pos': 1,
        'amp': 2,
        'fwhm': 3,
    }
    dataSet = asp.DataSet(dataDir)
    dataSet.load_database('autocal')
    # dataSet.plot_peaks()

    calibration_peaks = {}

    for wave, peakdict in dataSet.peakfitDict.items():
        peak_list = []
        peaks = peakdict['peaks']
        if len(peaks) == 0:
            continue
        # print(wave, peaks)
        for peak in peaks:
            # breakpoint()
            peak_list.append(Peaks(*peak))
        if len(peak_list) > 1:
            peak_list.sort(key=lambda x: x.amp)
        peak = peak_list[0]
        calibration_peaks[wave] = peak

    for key, value in calibration_peaks.items():
        print(key, value)
    breakpoint()
        


# series name - name of file
seriesName = 'autocal'
scriptDir = os.path.dirname(__file__)
dataDir = os.path.join(scriptDir, 'autocalibration')

# peakfit_autocal(scriptDir, dataDir)
generate_autocal(scriptDir, dataDir)
