from tucsen_camera import Plotter
import numpy as np
import os
from PIL import Image

def compare_noise():
    filepath = r'C:\Users\sjbrooke\OneDrive - The University of Melbourne\Data\Raman\tucsen\test-sulfur'
    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    plotter.crop_data((75,135))
    rawData = next(iter(plotter.dataDict.values()))

    plotter.average_all_data()
    plotter.dataDict['raw data'] = rawData
    # breakpoint()
    plotter.image_to_spectrum_all()

def main(filepath):

    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    # rawData = next(iter(plotter.dataDict.values()))
    # plotter.dataDict['raw data'] = rawData
    plotter.crop_data((75,135))

    plotter.average_all_data()
    # breakpoint()
    plotter.image_to_spectrum_all()
    # breakpoint()
    plotter.organise_data()
    plotter.subtract_BG()
    plotter.plot_all_spectra(binSize=10)
    # plotter.plot_images()
    




if __name__ == '__main__':
    filepath = r'C:\Users\Raman\Documents\LightField\Data\tucsen\V9 tests\20241218-160119898'
    filepath = r'C:\Users\sjbrooke\OneDrive - The University of Melbourne\Data\Raman\tucsen\test-sulfur'
    # compare_noise()
    main(filepath)