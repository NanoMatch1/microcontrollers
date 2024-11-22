import os
import numpy as np
from pixis_camera import PIXISCam
import time
import threading


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
        '''Acquires data for a specified time in seconds.'''


        start_time = time.time()
        # self.acquire_timestamp()
        while time.time() - start_time < self.runtime:
            timestamp = time.time() - start_time
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
        self.stop_continuous_acquire()
        # self.acquiring = True
        # self.acquire_thread = threading.Thread(target=self._timestamp_acquisition_loop)
        # self.acquire_thread.daemon = True  # Ensures the thread stops when the main program exits
        # self.acquire_thread.start()

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
    transientDir = 'transient'
    filename = 'test_data'
    dataCollection = DataCollection(saveDir, transientDir, filename)
    dataCollection.main()
