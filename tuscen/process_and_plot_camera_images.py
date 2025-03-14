from tucsen_camera import Plotter
import numpy as np
import os
from PIL import Image


# def main(filepath):
#     plotter = Plotter(dataDir=filepath)
#     plotter.load_all_data()
#     plotter.plot_images()
#     # plotter.crop_data((75,135))
#     plotter.take_second()
#     plotter.frames_to_spectrum()
#     plotter.save_all_data()

    # plotter.plot_all_spectra(binSize=1)
from matplotlib import pyplot as plt

def perform_gain_test(filepath):
    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    plotter.plot_all_spectra(binSize=1)
    breakpoint()



    # plotter.plot_all_spectra(binSize=1)

def pre_process_images_nice(filepath, crop=(2, -2), show=False):

    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    plotter.crop_data(crop_range=None)
    if show:
        plotter.plot_images()
    plotter.take_second()
    newDict = {}


    for file, data in plotter.dataDict.items():

        summed_array = np.average(data[crop[0]:crop[1]], axis=0)
        newDict[file] = summed_array
        if show:
            plt.plot(range(len(summed_array)), summed_array, label="Summed array")
            plt.title(file)
            plt.legend()
            plt.show()
    
    plotter.dataDict = newDict
    # plotter.frames_to_spectrum()
    plotter.subtract_background()
    plotter.save_all_data()
    
def pre_process_images(filepath):

    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    plotter.crop_data(crop_range=None)
    # plotter.plot_images()
    plotter.take_second()
    data = next(iter(plotter.dataDict.values()))
    # new_data = np.zeros((len(data[:, 0]), len(data[0, :]))
    for idx in range(len(data[:, 0])):
        row = data[idx, :]
        dataX = list(range(len(row)))
        dataY = row
        sumY = sum(dataY)
        print(f"Sum of row {idx}: {sumY}")
        print(idx)
        if 50 < idx < 90:

            # breakpoint()
            plt.plot(dataX, dataY, label = f"Row {idx}")
            plt.show()
    
    summed_array = np.sum(data[35:50], axis=0)
    plt.plot(dataX, summed_array, label="Summed array")

    plt.legend()
    plt.show()    
            
    breakpoint()
    plotter.frames_to_spectrum()
    plotter.save_all_data()

def plot_exported_data(filepath):
    filepath = os.path.join(filepath, 'export')
    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    # breakpoint()
    breakpoint()
    plotter.normalise_all_data(norm_range=(840, 1200))
    plotter.plot_all_spectra(binSize=1, offset=1)
    plotter.plot_all_subplots()

    # plotter.plot_all_spectra(binSize=1)

def new_image_process(filepath):
    plotter = Plotter(dataDir=filepath)
    plotter.load_all_data()
    # plotter.crop_data(crop_range=None)
    # plotter.take_second()
    # plotter.frames_to_spectrum()
    # plotter.save_all_data()
    plotter.plot_images()
    # plotter.plot_all_spectra(binSize=1)

# cfg2, gain0 is the winner

if __name__ == '__main__':
    filepath = r'C:\Users\Raman\matchbook\microcontrollers\tuscen\data\tucsen'
    filepath = r'C:\Users\Raman\matchbook\microcontrollers\tuscen\data\tucsen\19-2'
    filepath = r'C:\Users\Raman\matchbook\microcontrollers\tuscen\data\tucsen\07-03'
    # filepath = r'C:\Users\Raman\matchbook\microcontrollers\tuscen\data\tucsen'
    filepath = r'C:\Users\Raman\matchbook\microcontrollers\tuscen\data\savetests'
    # filepath = r'C:\Users\Raman\matchbook\microcontrollers\tuscen\data\gain_test'
    # perform_gain_test(filepath)
    # main(filepath)
    # pre_process_images_nice(filepath, crop=(90,110), show=False)
    new_image_process(filepath)
    # plot_exported_data(filepath)