from tucsen_camera import Plotter
import numpy as np
import os
from PIL import Image


def main(filepath):
    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    # plotter.plot_images()
    # plotter.crop_data((75,135))
    plotter.take_second()
    plotter.frames_to_spectrum()
    plotter.save_all_data()

    # plotter.plot_all_spectra(binSize=1)


def pre_process_images(filepath):

    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    # plotter.plot_images()
    # plotter.crop_data((75,135))
    plotter.take_second()
    plotter.frames_to_spectrum()
    plotter.save_all_data()

def plot_exported_data(filepath):
    filepath = os.path.join(filepath, 'export')
    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    plotter.plot_all_spectra(binSize=1)

    # plotter.plot_all_spectra(binSize=1)




if __name__ == '__main__':
    filepath = r'C:\Users\Raman\matchbook\microcontrollers\tuscen\data\gain_test'
    # main(filepath)
    pre_process_images(filepath)
    plot_exported_data(filepath)