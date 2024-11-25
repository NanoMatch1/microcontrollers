import os
import numpy as np
from pixis_camera import PIXISCam
import time
import threading
import matplotlib.pyplot as plt

def rename_files(fileDir, oldKey: str, newKey: str, extension='.txt'):
    '''rename files in dir that contain oldKey. Replaces oldKey with newKey in the filename.'''

    files_in_dir = [file for file in os.listdir(fileDir) if oldKey in file]
    # breakpoint()
    if len(files_in_dir) > 0:

        for file in files_in_dir:
            newFile = file.replace(oldKey, newKey)
            os.rename(os.path.join(fileDir, file), os.path.join(fileDir, newFile))
        
        print(f'{len(files_in_dir)} files renamed in {fileDir}.')
    

class SpectrumObject:

    dataType = 'spectrum'

    def __init__(self, dataDict, basename):
        self.basename = basename
        self.dataDict = dataDict

    def __repr__(self):
        return f"SpectrumObject({self.basename})"

class SeriesObject:

    '''Takes a dataDict containing data objects (e.g. SpectrumObject) and the basename for the series..'''

    dataType = 'series'

    def __init__(self, dataDict, basename):
        self.basename = basename
        self.seriesDict = dataDict

    def __repr__(self):
        return f"SeriesObject()"

class DataProcessing:

    '''Overall class for processing data from the camera. Operates on a dictionary of SeriesObjects containing spectrum objects.'''

    def __init__(self, saveDir):
        self.fileDir = saveDir
        self.dataDict = {}
        self.peakData = None

        self.load_files()
        self.load_wavelength_reference('wavelengths.csv')
        self.process_data()

    def load_wavelength_reference(self, filename):
        '''Loads the data with the wavelength reference.'''

        with open(os.path.join(self.fileDir, filename), 'r') as file:
            data = file.readlines()
            # data = data.split(r'\n')
            # data = data.strip('\n, \t')
        data = [x.strip('\n, \t') for x in data]
        data = [x.split(',') for x in data]
        data = np.array(data).astype(float)
        self.wavelength = data[:, 0]

        return self.wavelength


    def load_files(self):
        try:
            self.files = [file for file in os.listdir(self.fileDir) if file.lower().endswith('.npy')]
        except FileNotFoundError:
            self.fileDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.fileDir)
            self.files = [file for file in os.listdir(self.fileDir) if file.lower().endswith('.npy')]

        for file in self.files:
            filepath = os.path.join(self.fileDir, file)
            data = np.load(filepath)
            self.dataDict[file] = data
        return self.dataDict

    def parse_filename(self, filename, indexA="_", indexB="_"):
        '''Parses the filename to extract the relevant information between indexA and indexB.'''
        basename = filename.split(indexA)[0]
        substring = filename.split(indexA)[1]
        substring = substring.split(indexB)[0]

        return basename, substring
    
    def parse_timestamp(self, filename):
        '''Parses the filename to extract the timestamp.'''
        return self.parse_filename(filename, indexA='_', indexB='.npy')
    
    def process_data(self):
        newDict = {}
        seriesDict = self.sort_files()
        self.dataDict = self.process_timestamps(seriesDict)




        # for filename, data in self.dataDict.items():
        #     data = np.array(data).astype(float)
        #     # timestamp = self.parse_timestamp(filename)
        #     newDict[timestamp] = data
        

        return 
    
    def extract_peaks(self):

        self.peak_label_dict = {
            'p1': {'peak': 864.046, 'width': 2},
            'p2': {'peak': 869.772, 'width': 2},
            'p3': {'peak': 888.305, 'width': 2},
            'p4': {'peak': 900.526, 'width': 2},
            'v1': {'peak': 879.313, 'width': 2}

            # 'p2': 869.772,
            # 'p3': 888.305,
            # 'p4': 900.526,
            # 'v1': 879.313

        }

        indexDict = {}

        for series, dataDict in self.dataDict.items():
            if series not in indexDict.keys():
                indexDict[series] = {}
            for timestamp, data in dataDict.items():
                dataY = data[:, 1]
                dataX = data[:, 0]
                if timestamp not in indexDict[series].keys():
                    indexDict[series][timestamp] = {}
                for key, params in self.peak_label_dict.items():
                    value = params['peak']
                    width = params['width']
                    index = np.abs(dataX - value).argmin()
                    peak_average = np.mean(dataY[index-width:index+width])
                    indexDict[series][timestamp][key] = peak_average


        self.peakData = indexDict

    def generate_ratio_series(self, a='p1', b='p2'):
        if self.peakData is None:
            self.extract_peaks()
        
        ratio_dict = {series: [] for series in self.peakData.keys()}
        for series, dataDict in self.peakData.items():
            newArray = []
            for timestamp, data in dataDict.items():
                # breakpoint()
                ratio = data[a]/data[b]
                newArray.append([timestamp, ratio])

            newArray.sort(key=lambda x: x[0])

            newArray = np.array(newArray).astype(float)
            ratio_dict[series] = newArray

        self.ratioDict = ratio_dict

    def plot_ratio_series_simple(self):
        '''Create an interactive plot that loads the full spectrum when the user clicks on a point in the scatter graphs.'''

        fig, ax = plt.subplots(len(self.ratioDict), 1)
        for index, (series, data) in enumerate(self.ratioDict.items()):
            ax[index].scatter(data[:, 0], data[:, 1], label=series)
            ax[index].legend()
        plt.show()

    def plot_ratio_series(self):
        """
        Create an interactive plot that loads the full spectrum when the user
        clicks on a point in the scatter graphs.
        """
        # Create a figure with two subplots
        fig, axs = plt.subplots(len(self.ratioDict), 1, figsize=(8, len(self.ratioDict) * 3))
        if len(self.ratioDict) == 1:  # Ensure axs is iterable for a single subplot
            axs = [axs]
        
        # Store scatter plot data and mapping
        scatter_plots = []
        scatter_data = []  # To map click events to scatter points and series
        
        # Plot scatter plots for each series
        for index, (series, data) in enumerate(self.ratioDict.items()):
            scatter = axs[index].scatter(data[:, 0], data[:, 1], label=series, picker=True)
            axs[index].legend()
            axs[index].set_title(series)
            scatter_plots.append(scatter)
            scatter_data.append((series, data))
        
        # Create a new figure for displaying the spectrum
        spectrum_fig, spectrum_ax = plt.subplots(figsize=(8, 6))
        spectrum_ax.set_title("Selected Spectrum")
        spectrum_ax.set_xlabel("Wavelength")
        spectrum_ax.set_ylabel("Intensity")
        
        def on_click(event):
            # Check if the click is on a scatter point
            for i, scatter in enumerate(scatter_plots):
                if event.inaxes == scatter.axes:  # Ensure we're in the right subplot
                    series, data = scatter_data[i]
                    mouse_x, mouse_y = event.xdata, event.ydata
                    
                    # Find the nearest point
                    distances = np.sqrt((data[:, 0] - mouse_x)**2 + (data[:, 1] - mouse_y)**2)
                    nearest_idx = np.argmin(distances)
                    
                    # Retrieve the corresponding timestamp and load the spectrum
                    timestamp = data[nearest_idx, 0]
                    spectrum = self.dataDict[series][timestamp]  # Assuming dataDict holds original spectra
                    
                    # Plot the spectrum in the second figure
                    spectrum_ax.clear()
                    spectrum_ax.plot(spectrum[:, 0], spectrum[:, 1], label=f"Timestamp: {timestamp}")
                    spectrum_ax.legend()
                    spectrum_ax.set_title(f"{series} Spectrum at Timestamp {timestamp}")
                    spectrum_fig.canvas.draw_idle()
                    break

        # Connect the click event
        fig.canvas.mpl_connect("button_press_event", on_click)
        
        # Show the plots
        plt.show()

    def check_peak_calculations(self):
        '''Run to check that the peak averages extracted match the actual spectral data. Randomly selects 6 spectra and adds the peak positions and values with labels as markers on the graphs.FIX:not yet implemented.'''
        
        series = next(iter(self.dataDict.keys()))
        timeList = list(self.dataDict[series].keys())
        timeList = np.random.choice(timeList, 6)

        for series, dataDict in self.dataDict.items():
            for timestamp, data in dataDict.items():
                if timestamp in timeList:
                    plt.plot(data[:, 0], data[:, 1], label=timestamp)
                    for key, value in self.peakData[series][timestamp].items():
                        plt.plot(value, data[np.abs(data[:, 0] - value).argmin(), 1], 'ro', label=key)
            peakDict = self.peakData[series]
            # breakpoint()

            for timestamp, peaks in peakDict.items():
                if timestamp in timeList:
                    for key, value in peaks.items():
                        peak_pos = self.peak_label_dict[key]['peak']

                        plt.scatter([peak_pos], [value], 'ro', marker='x')

                        # create a text label for the peak
                        plt.text(peak_pos, value, key, fontsize=9)

            


                # plt.plot(peak, value, 'ro', label=peak)
                    
            plt.legend()
            plt.show()


    
    def export_data(self, basename=None, exportDir=None):

        '''exports the data to a format that can be handled by other scripts'''

        if exportDir is None:
            exportDir = os.path.join(self.fileDir, 'exported')
        if not os.path.exists(exportDir):
            os.makedirs(exportDir)

        for seriesName, dataDict in self.dataDict.items():
            if not os.path.exists(os.path.join(exportDir, seriesName)):
                os.makedirs(os.path.join(exportDir, seriesName))
            if basename is None:
                basename = seriesName
            for timestamp, data in dataDict.items():
                new_filename = f'{basename}_{timestamp}_{seriesName}.txt'
                
                filePath = os.path.join(exportDir, seriesName, new_filename)
                np.savetxt(filePath, data, delimiter=',')

            print(f'{seriesName} exported to {os.path.join(exportDir, seriesName)}.')
    
    def sort_files(self):
        seriesDict = {}
        for filename, data in self.dataDict.items():
            # sorted_filenames = sorted(self.files, key=lambda x: float(self.parse_timestamp(x)))
            basename, extra = self.parse_filename(filename)
            if basename not in seriesDict:
                seriesDict[basename] = {extra: data}
            else:
                seriesDict[basename][extra] = data

        return seriesDict

    def process_timestamps(self, seriesDict):
        newDict = {}
        for seriesName, dataDict in seriesDict.items():
            if seriesName not in newDict.keys():
                newDict[seriesName] = {}
            for info, data in dataDict.items():
                timestamp = info.split('.npy')[0]
                timestamp = float(timestamp)
                newData = np.column_stack((self.wavelength, data))
                newDict[seriesName][timestamp] = newData

        self.dataDict = newDict
        return self.dataDict
        

    

class DataCollection:

    def __init__(self, saveDir, transientDir, filename):
        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.saveDir = saveDir
        self.transientDir = transientDir
        self.filename = filename
        self.acquiring = False
        self.acquire_thread = None
        self.runtime = 0

        self.comdict = {
            'acquire': self.acquire_spectrum,
            'run': self.continuous_acquire,
            'stop': self.stop_continuous_acquire,
            'filename': self.set_filename,
            'debug': self.debug,
            'acqtime': self.camera_set_acquisition_time,
            'go': self.acquire_timestamp,
            'gofix': self.acquire_for_some_time,
            'runtime': self.set_runtime
        }

        self.initialise()
        self.camera = PIXISCam(self)

    def set_runtime(self, runtime):
        self.runtime = float(runtime)

    def acquire_for_some_time(self):
        '''Acquires data for a specified time in seconds. Blocks until acquisition is complete.'''

        start_time = time.time()
        while time.time() - start_time < self.runtime:
            timestamp = time.time() - start_time
            data = self.camera.acquire_one_frame()
            np.save(os.path.join(self.transientDir, "transient_data.npy"), data)  # save to transient dir for immediate plotting/viewing

            data = np.array(data, dtype=np.int32)  # convert to numpy array for fast saving
            filename = os.path.join(self.saveDir, f'{self.filename}_{timestamp:.2f}.npy')
            np.save(filename, data)

        self.stop_continuous_acquire()
        print("Acquisition complete.")


    def camera_set_acquisition_time(self, time):
        restart = False
        if self.acquiring:
            self.stop_continuous_acquire()
            restart = True
        self.acq_time = float(time) * 1000  # ms
        self.camera.cam.set_attribute_value("Exposure Time", self.acq_time)
        if restart:
            self.continuous_acquire()

    def set_filename(self, filename):
        self.filename = filename

    def initialise(self):
        self.saveDir = os.path.join(self.scriptDir, self.saveDir)
        self.transientDir = os.path.join(self.scriptDir, self.transientDir)

        if not os.path.exists(self.saveDir):
            os.makedirs(self.saveDir, exist_ok=True)
        if not os.path.exists(self.transientDir):
            os.makedirs(self.transientDir, exist_ok=True)

    def debug(self):
        breakpoint()

    def acquire_timestamp(self, runtime=None):
        '''Starts acquisition and timestamps each filename in a separate thread.'''
        

        inital_time = time.time()
        if self.acquire_thread and self.acquire_thread.is_alive():
            print("Acquisition is already running.")
            return

        self.acquiring = True
        self.acquire_thread = threading.Thread(target=self._timestamp_acquisition_loop)
        self.acquire_thread.daemon = True  # Ensures the thread stops when the main program exits
        self.acquire_thread.start()

    def _timestamp_acquisition_loop(self):
        '''Handles the continuous acquisition process with timestamps.'''

        start_time = time.time()
        try:
            while self.acquiring:
                if self.runtime and time.time() - start_time > self.runtime:
                    self.stop_continuous_acquire()
                    print("Acquisition complete.")
                    break
                data = self.acquire_spectrum(save=False)
                timestamp = time.time() - start_time
                np.save(os.path.join(self.saveDir, f'{self.filename}_{timestamp:.2f}.npy'), data)
                time.sleep(0.1)  # Adjust as needed to prevent overloading
        except Exception as e:
            print(e)
            time.sleep(self.acq_time)

    def acquire_spectrum(self, overwrite=False, save=True):
        '''Acquires a single spectrum and saves it in the saved_data directory.'''
        print("Acquiring...")
        data = self.camera.acquire_one_frame()
        np.save(os.path.join(self.transientDir, "transient_data.npy"), data)  # save to transient dir for immediate plotting/viewing

        data = np.array(data, dtype=np.int32)  # convert to numpy array for fast saving
        if not overwrite:
            file_index = len([x for x in os.listdir(self.saveDir) if x.split('_')[0] == self.filename])
        else:
            file_index = 0


        while True:
            try:
                if save:
                    filename = os.path.join(self.saveDir, f'{self.filename}_{file_index}.npy')
                    np.save(filename, data)
                return data
            except PermissionError:
                print('File in use. Waiting 0.1 s...')
                time.sleep(0.1)
                continue


    def continuous_acquire(self):
        '''Starts continuous acquisition in a separate thread.'''
        if self.acquire_thread and self.acquire_thread.is_alive():
            print("Continuous acquisition is already running.")
            return

        self.acquiring = True
        self.acquire_thread = threading.Thread(target=self._continuous_acquisition_loop)
        self.acquire_thread.daemon = True
        self.acquire_thread.start()

    def _continuous_acquisition_loop(self):
        '''Handles continuous acquisition process.'''
        self.camera.start_continuous_acquisition()
        while self.acquiring:
            time.sleep(0.1)  # Maintain responsiveness

    def stop_continuous_acquire(self):
        '''Stops the continuous acquisition of the camera.'''
        self.acquiring = False
        if self.acquire_thread:
            self.acquire_thread.join()
        self.camera.stop_continuous_acquisition()

    def process_command(self, command):
        '''Processes the command from the user.'''
        command = command.split(' ')
        if command[0] not in self.comdict:
            print('Command {} not recognised. Try again.'.format(command))
            return
        try:
            if len(command) == 1:
                self.comdict[command[0]]()
            elif len(command) > 1:
                self.comdict[command[0]](*command[1:])
        except Exception as e:
            print(e)

    def main(self):
        '''Get input from user, and run the appropriate function.'''
        while True:
            command = input('Enter command: ')
            if command == 'exit':
                self.stop_continuous_acquire()
                break
            self.process_command(command)


if __name__ == '__main__':
    saveDir = 'spectroscopy_saved_data'
    saveDir = r'C:\Users\sjbrooke\OneDrive - The University of Melbourne\Data\Maria\spectroscopy_saved_data'
    transientDir = 'transient'
    filename = 'test_data'
    saveDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), saveDir)
    # rename_files(saveDir, "0.2C-NDNC0.5C_", "0.2C-NDNC0.5C-A_")
    # rename_files(saveDir, "NR_", "NR-")
    # dataCollection = DataCollection(saveDir, transientDir, filename)
    # dataCollection.main()
    dataProcessing = DataProcessing(saveDir)
    dataProcessing.generate_ratio_series()
    dataProcessing.plot_ratio_series()  
    # dataProcessing.check_peak_calculations()
    breakpoint()
    # dataProcessing.export_data(basename="LnNP")
