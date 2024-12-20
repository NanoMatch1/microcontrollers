from tucsen_camera import Plotter
import numpy as np
import os
from PIL import Image


def main(filepath):

    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    rawData = next(iter(plotter.dataDict.values()))

    plotter.average_all_data()
    breakpoint()
    plotter.crop_data((75,135))
    plotter.plot_all_spectra(binSize=8)
    # plotter.plot_images()
    plotter.organise_data()
    




if __name__ == '__main__':
    filepath = r'C:\Users\Raman\Documents\LightField\Data\tucsen\V9 tests\20241218-160119898'
    filepath = r'C:\Users\sjbrooke\OneDrive - The University of Melbourne\Data\Raman\tucsen\test-sulfur'

    main(filepath)