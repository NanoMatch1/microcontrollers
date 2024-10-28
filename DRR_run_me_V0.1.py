import os
import numpy as np
import serial
import time
import pyvisa
import threading
import json
import traceback
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import tkinter as tk

from tkinter import ttk
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from types import SimpleNamespace
from dataclasses import dataclass
from pixis_camera import PIXISCam



'''# looking for some kind of response like "b" or "o". Use command "O2000" to enter into command mode.
# Polyfit calibration 24/08/27: [-1.28255101e-02 -4.23233709e+01  4.22414334e+04]
Initial grating is Blaze 500, 1200 g/mm
centre for 532 nm is roughly 241543
centre for sulfur at ~800 nm is 376886 (apd laser at "370686"/371736) (NEW 23/05 375131) (ccd+= 6000) 374414
List of useful commands = {
"Initiate command mode": "02000",
# "Initialise Spectrometer: "A",
"read motor position": "H0",
"read slit position: "j0,0",
"move slit relative: "k0,0,100"
"poll motors after move command sent - necessary because control is given to PC immediately after command is given, but new motor command cannot be issued until motor motion is stopped. Implement a check for this here. Note if the motors are not busy, a timeout is received... could be a delay/timing issue: "E",
"move exit mirror to front exit (out of path): "f0".
"move exit mirror to side exit (in path): "e0",
"entrance mirror to front enterance: "c0",
"entrance mirror to side enterance: "d0"


'''


# def poly_sin_modulation_fit(x, a2, a1, a0, A, B, C, D):
#     # Polynomial part
#     poly = a2 * x**2 + a1 * x + a0
#     # Sinusoidal modulation part
#     modulation = A * np.sin(B * x + C) + D
#     return poly + modulation

class PolySinModulation:
    def __init__(self, a2, a1, a0, A, B, C, D):
        """
        Initialize the polynomial and sinusoidal coefficients.
        Polynomial: a2*x^2 + a1*x + a0
        Sinusoidal modulation: A*sin(B*x + C) + D
        """
        self.a2 = a2
        self.a1 = a1
        self.a0 = a0
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def __call__(self, x):
        """
        Evaluate the polynomial + sinusoidal modulation at the given x value.
        """
        poly = self.a2 * x**2 + self.a1 * x + self.a0
        modulation = self.A * np.sin(self.B * x + self.C) + self.D
        return poly + modulation

    def __repr__(self):
        """
        String representation of the polynomial and sinusoidal components.
        """
        poly_part = f"{self.a2}*x^2 + {self.a1}*x + {self.a0}"
        sin_part = f"{self.A}*sin({self.B}*x + {self.C}) + {self.D}"
        return f"PolySinModulation: ({poly_part}) + ({sin_part})"

class LinSinModulation:
    '''Class for linear + sinusoidal modulation fit.'''
    def __init__(self, a1, a0, A, B, C, D):
        self.a1 = a1
        self.a0 = a0
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def __call__(self, x):
        linear = self.a1 * x + self.a0
        modulation = self.A * np.sin(self.B * x + self.C) + self.D
        return linear + modulation
    
    def __repr__(self):
        linear_part = f"{self.a1}*x + {self.a0}"
        sin_part = f"{self.A}*sin({self.B}*x + {self.C}) + {self.D}"
        return f"LinSinModulation: ({linear_part}) + ({sin_part})"



class GUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Arduino Command Interface")

        # Setup the serial connection
        self.microscope = Microscope()


class DynamicPlotApp:
    def __init__(self, master):
        self.master = master
        master.title("Dynamic Plotting with Tkinter")

        # Create a matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.lines, = self.ax.plot([], [], 'r-')  # Lines to plot
        self.ax.set_xlim(0, 100)  # Set x-axis limit
        self.ax.set_ylim(0, 10)  # Set y-axis limit

        # Embed the plot in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Initialize plot data
        self.x_data = []
        self.y_data = []

        # Add a button to update the plot
        # self.update_button = ttk.Button(master, text="Update Plot", command=self.update_plot)
        # self.update_button.pack()

    def update_plot(self, data):
        # Simulate new data coming in
        # new_x = len(self.x_data) + 1
        # new_y = np.random.rand()

        # Update the data
        self.x_data.append(data[0])
        self.y_data.append(data[1])

        # Update the plot
        self.lines.set_data(self.x_data, self.y_data)
        # self.ax.set_xlim(min(self.x_data), max(self.x_data))  # Optionally adjust limits dynamically
        self.canvas.draw()


    

class DualMonochromator:

    def __init__(self, microscope):
        self.microscope = microscope
        self.get_motor_positions()

        self.current_mode = 'additive'
        self.current_pos = (0, 0)

    def get_motor_positions(self):
        response = self.microscope.process_coms('Cgetinfo')
        if response == 'NONE':
            initial_pos = self.current_pos()
            home_pos = self.home_motors()

    
    def home_motors(self):
        response = self.microscope.process_coms('Chome')
        self.current_pos = (0, 0)
        return response
    
    def calibration_1(self, wavelength):
        return # function from calibration file, creating a position in steps for motor 1
    
    def calibration_2(self, wavelength):
        return # function from calibration file, creating a position in steps for motor 2
    
    def move_to(self, target_pos):
        motor_1_pos = self.calibration_1(target_pos)
        motor_2_pos = self.calibration_2(target_pos)

        response = self.microscope.process_coms('Cmove {} {}'.format(motor_1_pos, motor_2_pos))
        if response == 'OK':
            self.current_pos = (motor_1_pos, motor_2_pos)
        else:
            print('Error moving monochromator motors')
            print(response)
        pass

    def load_calibrations(self):
        if self.current_mode == 'additive':
            # load additive calibration file
            # self.load_additive_calibration()
            # Shoudl contain calibration for motor 1 and motor 2
            pass
        elif self.current_mode == 'subtractive':
            # load subtractive calibration file
            pass
            # self.load_subtractive_calibration()
            # Should contain calibration for motor 1 and motor 2
    

        


    def add_mode(self):
        pass

'''Code plan.
Make dual monochromator class. The mono should know what mode it is in based on a current or previous format. 
The class is a wrapper for communication with an individual microcontroller. 
1. It should, on initialisation, send a message to the microcontroller and request motor positions and current mode.
    a. the current mode should be conveyed to the microcontroller and stored there
2. if the microcontroller does not have the required information (such as during boot), the mono should home itself.
    a. before homing, it should save the current position, so that it can return here, including backlash compensation.
3. all motors should operate under a backlash compensation regime, and approach the target position from the same direction.
4. the mono should have a method for moving to a target position, and a method for moving to a target wavelength. 
    a. in Additive mode, Target wavelength will be the primary method for moving the mono.
    b. in subtractive mode, the target wavelength will also be the primary method for moving, but in this case the target wavelength needs to be BLOCKED rather than transmitted.
        i. therefore, a two calibration files need to be stored, one for each mode. In additive, the calibration tells the code what wavelength transmission correspons to what motor position. In subtractive, the calibration tells the code what motor position causes the desired wavelength to be blocked.
        ii. there should be a correction factor which allows one to get closer to the laser line. The correction factor applied will be in units of wavenumbers, which are calibrated to steps by the calibration file.
5. for safety, the mono class should only allow movement of the motors when the beam is blocked. This can be achieved by having a method which checks the beam status within the microscope class, and if the beam is not blocked, it will block the beam and then move the motors.

there will be homing motors that the monochromator should.'''


# class Calibrations:

#     def __init__(self, calibrations):
#         self.coefficients = calibrations
#         # self.__dict__.update(np.poly1d(calibrations))
#         self.__dict__.update({calib: np.poly1d(self.coefficients[calib]) for calib in self.coefficients})
        
'''Items still to do:
Phase 1: High priority
    1. Add shutter for safety. Use single power mosfet to feed 3-5V power to the shutter.
        a. Edit the pinhole shutter method to drive this shutter.
    2. Bring PICAM interface into the microscope. Use a separate class and feed it to the microscope class/microscope class to it.
    2. Create methods for:
        a. Acquiring a spectrum of a given range. This requires multiple scans and stitching them together. Note this can now be done internally using the PICAM interface
            i. write triax control code. needs polling method for moving motors
            i. This requires a data save method. use the ui to enter a filename, and save the data to a file.
        b. a basic laser excitation scan. This will simply acquire a spectrum at a range of wavelengths with a given resolution.
            i. make the scan method agnistic, so it can be used in the final version of the multidiemensional scans.
        c. Create a method for exporting a map of the data structure. This should eventually accommodate multi-dimensional data including wavelength, position, and polarization.

 >>> Start scanning MoS2 powder

Phase 2: In preparation of scanning MoS2 flakes
    1. Add motor control for the sample stage.
    2. Enclose system.
    3. Add input polarization control.
    4. Add output polarization control.
    5. Create multidimensional scan method.
    6. Motorise L3. Create calibration for L3.

>>> Scan MoS2 flakes or WSe2 flakes

Phase 3: Polishing the system
    1. Create homing protocols for all motors.
    2. Add control of laser
    3. Try changing spectrometer control to RS232/MEGA UART
    4. Create all autocalibration methods.
    5. Try switch to linux
    6. Build single board computer for control
'''

@dataclass
class MotorPositions:
    x: int
    y: int
    z: int
    a: int

class Microscope:

    # calibration_backup = {"wl_to_triax_steps": [0.10804683994803718, 331.8588098129754, 43950.89354704326], "triax_steps_to_wl": [-5.094413299766325e-08, -0.01590813394008432, 802.7653861488677], "wl_to_l1": [-0.01252753345943214, -42.75470684410267, 42395.08424620002], "l1_to_wl": [-5.094413299758575e-08, -0.015908133940084567, 802.765386148867], "wl_to_l2": [0.004068479941637935, 20.30418040830074, -18891.41344719332], "l2_to_wl": [-2.1134374286916415e-07, 0.03727793396921931, 801.6492620060089], "wl_to_g1_subtractive": [-0.0009343860392719734, 10.7261833692083, 650945.1172672338, 4.655494031296545, 0.08293861801416774, -28.836971874316305, -658973.3758272409], "g1_to_wl_subtractive": [-3.997416525894944e-06, 0.11504349729740472, 40924.95099077628, -3.7657797835191977, 0.0029830668481275646, 6.0959394773331725, -40119.77931396578], "wl_to_g2": [0.023079240005018726, -45.473382574917395, 8566.991143604224], "g2_to_wl": [4.023690443149823e-05, 0.9297669680984147, 6082.062394487625], "wl_to_g1_additive": [0.005183899414806875, 1.448578450504759, 624081.2598467232, 18.066764876201965, 0.08365631420139119, -29.51008752837752, -628605.1425510542], "g1_to_wl_additive": [-9.626148251565028e-06, 0.10420683828922353, -4848.442236579409, -2.272040105929268, 0.0074373346698996335, 6.471415416643864, 5653.535879138745]}

    # standard positions:
    # Current laser wavelength: 802.7494779639835
    # Current grating wavelength: 802.7823897229985

    ldr_scan_dict = {
        'l2': {
            'range': 150,
            'resolution': 5,
        },
        'g1': {
            'range': 150,
            'resolution': 5,
        },
        'g2': {
            'range': 150,
            'resolution': 5,
        }
    }
    

    def __init__(self, debug_skip=[], unoCOM='COM8'):

        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.scriptDir, 'data')
        self.transientDir = os.path.join(self.scriptDir, 'transient')
        self.saveDir = os.path.join(self.dataDir, 'saved_data')

        self.__build_directories()
        self.__generate_calibrations(report=True)

        self.scan_min = 800
        self.scan_max = 835
        self.scan_resolution = 0.5

        # self.grating_calib = calibrations['']

        self.grating_steps = None
        self.grating_wavelength = None
        self.laser_steps = None
        self.laser_wavelength = None
        self.triax_steps = None
        self.triax_wavelength = None

        self.current_wavelength = None
        self.current_shift = 0
        self.monochromator_mode = 'subtractive'
        self.pinhole = None
        self.save_pinhole = None
        self.detector_safety = True
        # self.current_motor_positions = {'A': {}, 'B': {}}
        # self.to_addivite = -12990 -13108+39 

        self.acq_time = 1
        self.current_filename = None
        self.centre_wavelength = 376886

        self.data = []

        self.microscope_functions = {
            'scan': self.run_scan_spectrum,
            'get_grating_position': self.get_grating_position,
            'scan_min': self.set_scan_min,
            'scan_max': self.set_scan_max,
            'scan_res': self.set_scan_resolution,
            'acq_time': self.set_acquisition_time,
            'sl': self.go_to_laser_wavelength,
            'sd': self.go_to_grating_wavelength,
            'st': self.go_to_triax_wavelength,
            'sall': self.go_to_wavelength_all,
            # 'shift': self.go_to_grating_wavelength,
            'wai': self.get_all_current_positions,
            'reference': self.reference_calibration,
            'shift': self.go_to_wavenumber,
            'calshift': self.simple_calibration_shift,
            'isrun': self.wait_for_motors,
            'report': self.report_status,
            'setmode': self.change_monochromator_mode,
            'writemotora': self.set_absolute_positions_A,
            'writemotorb': self.set_absolute_positions_B,
            'help': self.show_help,
            'motorscan': self.motor_scan,
            'lockcal': self.lock_calibration,
            'unlockcal': self.unlock_calibration,
            'pin': self.move_pinhole,
            'setpin': self.set_pinhole_pos,
            'mshut': self.close_mono_shutter,
            'mopen': self.open_mono_shutter,
            'readldr': self.read_ldr0,
            'debug': self.print_debug,
            'calibrate': self.run_calibration,
            'gtgsteps': self.go_to_grating_steps,
            'homemono': self.home_motors_monochromator,
            'camera': self.start_camera_ui, # for testing
            'pixelcal': self.calibrate_triax_pixels,
            'acquire': self.acquire_spectrum,
            'run': self.continuous_acquire,
            'stop': self.stop_continuous_acquire,
            # 'testacq': self.test_acquire_series,

            # 'changemode': self.change_monochromator_mode,
            # 'setpos': self.set_absolute_positions
            # additive reference at 220: [83, -13108...]

        }

        # commands for controlling TRIAX spectrometer
        self.spectrometer_dict = {
            'init': 'A',
            'comsmode': '02000',
            'read_grating': 'H0',
            'rg': 'H0',
            'grating': 'F0,',
            'mg': 'F0,',
            'read_enter': 'j0,0',
            'ren': 'j0,0',
            'read_exit': 'j0,3',
            'rex': 'j0,3',
            'move_enter': 'k0,0,',
            'men': 'k0,0,',
            'move_exit': 'k0,3,',
            'mex': 'k0,3,',
            'tpol': 'E', # poll motors after move command sent
            'ccd_mode': 'f0',
            'ccd': 'f0',
            'apd_mode': 'e0',
            'apd': 'e0',
            # 'gotoir': 'F0,375131'
            #'entrance mirror to front enterance': 'c0',
            #'entrance mirror to side enterance': 'd0'
        }

        # commands for sample/stage motion and imaging beamsplitter
        self.stage_dict = {
            # 'relative': 'relative',
            # 'absolute': 'absolute',
            # 'X': 'X',
            # 'Y': 'Y',
            # 'Z': 'Z',
            # 'imagemode': 'G0 E-500',
            # 'ramanmode': 'G0 E500'
        }

        self.dual_mono_dict = {
            'add_mode': 'additive',
            'sub_mode': 'subtractive',

        }

        # commands for controlling laser properties
        self.tuning_motor_dict = { # TODO: separate into Stage motion and laser tuning
            'lambda': 'lambda',
            'atest': 'Atest',
            'btest': 'Btest',
            'ctest': 'Ctest',
            'creport': 'Creport',
            'astatus': 'Astatus',
            'bstatus': 'Bstatus',
            'cstatus': 'Cstatus',
            'z': 'BZ',
            'y': 'BY',
            'x': 'BX',
            'a': 'BY', # TODO: BUG: Temporarilly ported A to Y for testing
            'g1': 'BX',
            'g2': 'BY',
            'l1' : 'AX',
            'l2' : 'AY',
            'setposa': 'Asetpos',
            'setposb' : 'Bsetpos',
            'aisrun': 'Aisrun',
            'bisrun': 'Bisrun',

            'getposa': 'Apos',
            'gpa' : 'Apos',
            'getposb': 'Bpos',
            'gpb' : 'Bpos',


        }

        # additive position: Y -12984, subtractive = 0

        self.acquisition_dict = {
            # 'acq': 'acq', 
            # 'run': 'run',
            'gsh': 'gsh',
            'rldr0': 'ld0'


        }

        self.laser_dict = {
            'warmup': '?WARMUP%',
            'idn': '?IDN',
            'diode': '?C1',
            'shutteron': 'SHUTTER:1',
            'shutteroff': 'SHUTTER: 0'
        }
#TODO: Add commands for moving steppers for laser gratings. (A)
# calibrate motors
# Add commands for moving stage motors (B)
# Add comms for turning laser on and off
# Write unit tests

        # Commands for handling the general state of the system
        self.general_dict = {
            'triax': self.connect_to_spectrometer,
            'laser': self.connect_to_laser,
            # 'camera': self.connect_to_camera,
        }
        # commands for controlling APD
        self.apd_dict = {
            # 'run': 'run',
            # 'acq': 'acq',
            # 'time': 'time',
        }

        if 'TRIAX' not in debug_skip:
            self.spectrometer, self.state = self.connect_to_spectrometer()
        # self.pico_marlin = self.connect_to_marlin()
        # self.apd_serial = self.connect_to_APD()
        if 'UNO' not in debug_skip:
            self.uno_serial = self.connect_to_UNO(unoCOM, baud=9600)
        if not 'laser' in debug_skip:
            self.laser_serial = self.connect_to_laser()
        if not 'camera' in debug_skip:
            self.camera = PIXISCam(self)
            
        # if not 'APD' in debug_skip:
        #     self.apd_serial = self.connect_to_APD()
        # time.sleep(1)
        # self.grating_pos = self.get_grating_position()

    # def pack_floats(self, floats):
    #     return b','.join(struct.pack('<f', f) for f in floats)

    # def connect_to_APD(self):
    #     APD_serial = serial.Serial('COM7', 9600, timeout=1)
    #     return APD_serial

        self.guess_mode()
        self.report_status()

        self.ammend_calibrations()
        # self.start_camera_ui()
        # self.process_coms('triax')

        # self.run_ldr0_scan()
        # self.run_calibration((800, 810), 5)

    def __build_directories(self):
        '''Builds all the directories required for the system to run.'''

        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)
        if not os.path.exists(self.transientDir):
            os.makedirs(self.transientDir)
        if not os.path.exists(self.saveDir):
            os.makedirs(self.saveDir)

    def go_to_wavelength_all(self, wavelength, shift=True):
        self.go_to_laser_wavelength(wavelength)
        # raman_shift = self.calculate_raman_shift_wavelength(wavelength)
        if shift is True:
            breakpoint()
            self.go_to_wavenumber(self.current_shift)
        else:
            self.go_to_grating_wavelength(wavelength)
        self.go_to_triax_wavelength(wavelength)

    def test_acquire_series(self):
        for _ in range(3):
            frame = self.camera.acquire_one_frame()
            time.sleep(1)
        
        print("finihsed")

    def stitch_spectrum(self, data, window):
        '''Takes a list of spectra in data and stitches them together in to one spectrum. The window is the size of the spectral shift in nm.'''
        #TODO: Need to first calibrate triax pixels to wavelength

        pass

    def start_camera_ui(self):
        self.camera.start_ui()

    def camera_set_acquisition_time(self, time):
        self.acq_time = float(time)*1000 #ms
        self.camera.cam.set_attribute_value("Exposure Time", self.acq_time)

    def camera_set_roi(self, y1, y2):
        '''Set the ROI assuming 2D binning across the whole chip (x_0 to x_1023).'''

        if y2 <= y1:
            print('Invalid ROI. y2 must be greater than y1.')
            return
        
        self.camera.cam.set_roi(0, 1023, y1, y2, 1, y2-y1)


    def calibrate_triax_pixels(self, start=750, stop=960, window=12):
        start = float(start)
        stop = float(stop)
        window = float(window)

        scan_range = np.arange(start, stop, window)

        dataDict = {}

        for wl in scan_range:
            self.go_to_triax_wavelength(wl)
            self.go_to_laser_wavelength(wl)
            self.go_to_grating_wavelength(wl)
            dataDict[wl] = self.acquire_calibrate_triax()

        self.pixelDict = dataDict

    # def calculate_window_shift(self, working_wavelength, window_shift=12):
    #     try:
    #         working_wavelength = float(working_wavelength)
    #         window_shift = float(window_shift)
    #     except ValueError:
    #         print('Invalid input')
    #         return
        
        
        


    def acquire_calibrate_triax(self, start=750, stop=960, window=12, save_files=True):
        '''Used to calibrate the wavelength per pixel across the spectrum. Required for any data collection. Acquires two spectra at either end of the CCD range and saves them to a file. The window is the size of the shift in nm.'''

        # starting_wavenumber = self.current_laser_wavenumber
        # starting_wavelength = self.current_laser_wavelength[0]
        # limit_wavelength = self.calculate_raman_shift_wavelength(raman_shift)
        
        data = {starting_wavelength: {}}
        # current_wavenumber = round(float(starting_wavenumber), 2)
        current_wavelength = float(starting_wavelength)

        count = 0

        while count < 2:
            self.go_to_triax_wavelength(current_wavelength)
            frame = self.camera.acquire_one_frame()
            data[starting_wavelength] = {current_wavelength: frame}
            # self.camera._update_plot(frame)
            current_wavelength += window
            count += 1
            # current_wavenumber = round(10_000_000/current_wavelength, 2)

        # self.latest_data = self.stitch_spectrum(raman_shift)
        # while 
        if save_files is True:
            for idx, frame in enumerate(data):
                with open(os.path.join(os.path.join(self.scriptDir, 'triax_calibration'), f'{idx}_triax-calibration_{window}nm.json'), 'w') as f:
                    json.dump(frame, f)
        return data
    
    def write_data_transient(self, data, filename):
        '''Writes the data to a file in the data directory for transient data.'''


    def acquire_spectrum(self):
        '''Acquires a single spectrum and saves it in the saved_data directory.'''

        data = self.camera.acquire_one_frame()
        data = np.array(data, dtype=np.int32) # convert to numpy array for fast saving
        file_index = len([x for x in os.listdir(self.saveDir) if x[:-4] == self.filename])
        filename = os.path.join(self.saveDir, self.current_filename, f'_{file_index}.npy')
        
        while True:
            try:
                np.save(filename, data)
                return data
            except PermissionError:
                print('File in use. Waiting 0.1 s...')
                time.sleep(0.1)
                continue

    def continuous_acquire(self):
        '''Runs the continuous acquisition of the camera and saves the data to the transient directory.'''
        self.camera.start_continuous_acquisition() # threaded for non-blocking use
        # self.camera.continuous_acquisition() # for debugging

    def stop_continuous_acquire(self):
        '''Stops the continuous acquisition of the camera.'''
        self.camera.stop_continuous_acquisition()

    # def save_transient_data(self, data):
    #     np.save(os.path.join(self.transientDir, 'transient_data.npy'), data)


    def acquire_spectrum_step_scan(self, raman_shift=250, window=12):
        '''Takes the number of spectra required to cover the specified raman_shift. Converts shifts to wavelength using the current laser position in order to compensate for the non-linear dispersed spectral window. i.e. longer wavelengths disperse more.'''
        starting_wavenumber = self.current_laser_wavenumber
        # starting_wavelength = self.current_laser_wavelength
        limit_wavelength = self.calculate_raman_shift_wavelength(raman_shift)
        
        data = []
        current_wavenumber = round(float(starting_wavenumber), 2)
        current_wavelength = float(starting_wavelength)

        while current_wavelength < limit_wavelength:
            self.go_to_triax_wavelength(current_wavelength)     
            data.append([current_wavenumber, self.cam.acquire_one_frame()])
            current_wavelength += window
            current_wavenumber = round(10_000_000/current_wavelength, 2)

        # self.latest_data = self.stitch_spectrum(raman_shift)
        # while 
        return data


    def get_triax_steps(self):
        '''Polls the spectrometer for position and returns the current position in steps.'''
        response = self.process_coms('rg')
        self.triax_steps = int(response.strip()[1:])
        return self.triax_steps

    def calculate_triax_wavelength(self, steps=None):
        '''Calculates the wavelength that would appear at pixel 50 (as per the calibration file) for the given steps.'''
        if steps is None:
            steps = self.get_triax_steps()
        self.triax_wavelength = self.calibrations.triax_steps_to_wl(steps)
        return self.triax_wavelength

    def go_to_triax_wavelength(self, wavelength: float, autoshutter=False):
        '''Moves the triax spectrometer to the specified wavelength that would appear at pixel 50 (as per the calibration file).'''
        try:
            wavelength = float(wavelength)
        except ValueError:
            print('Invalid input')
            return
        
        triax_steps = self.get_triax_steps()
        
        target_steps = round(self.calibrations.wl_to_triax_steps(wavelength))
        # breakpoint()
        new_steps = target_steps - triax_steps
        # return if no movement is required
        if new_steps == 0:
            return
        
        print('UNO>g {}>triax'.format(new_steps))
        response = self.process_coms('mg {}'.format(new_steps))
        if response == 'o':
            triax_res = self.wait_for_triax(target_steps)
            if triax_res == 'S0':
                print('Triax moved to {} nm'.format(wavelength))
                self.triax_steps = target_steps
                return 'S0'
            else:
                print('Triax move failed: {}'.format(triax_res))
                return 'F0'

        else:
            print('Triax communication failed:')
            print(response)

    def wait_for_triax(self, target_steps, timeout=10):
        '''Polls the spectrometer until the target steps are reached. Note the MOTOR BUSY CHECK (E) on the spectrometer does not send a response with this configuration, so we use this command instead.'''
        start = time.time()
        while True:
            response = self.get_triax_steps()
            if response == target_steps:
                return 'S0'
            time.sleep(0.1)
            if time.time() - start > timeout:
                print('Timeout reached')
                return 'F0'

    def home_motors_monochromator(self):
        response = self.process_coms('Bhome')
        return response


    def calculate_overhead(self):
        acq_times = [0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 0.128, 0.256, 0.512, 1.024]
        time_overhead = []
        for val in acq_times:
            start = time.time()
            for i in range(10):
                self.process_coms(f'acq {val}')
            end = time.time()
            time_overhead.append([val, (end-start)/10])
        
        print(time_overhead)
        # breakpoint()


    def run_calibration(self, motor:str, wavelength_range=(750, 850), resolution=5):
        if motor.lower() not in ['g1', 'g2', 'l2']:
            print("Invalid motor. Must be 'g1' or 'g2' or 'l2'")
            return

        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()  # Convert NumPy arrays to Python lists
            elif isinstance(obj, np.int32) or isinstance(obj, np.int64):
                return int(obj)  # Convert NumPy integers to Python ints
            elif isinstance(obj, np.float32) or isinstance(obj, np.float64):
                return float(obj)  # Convert NumPy floats to Python floats
            else:
                return obj  # Leave other types unchanged
            

        calibrationDict = {'data_type': 'autocal'}

        if isinstance(wavelength_range, str):
            vals = wavelength_range.split(',')
            wavelength_range = (float(vals[0]), float(vals[1]))

        resolution = float(resolution)

        initial_grating = self.grating_steps
        initial_laser = self.laser_steps

        wavelengths = np.arange(*wavelength_range, resolution)
        print(f"Running {motor} calibration for wavelengths: ", wavelengths)
        cond = input("Continue? (y/n): ")
        if cond.lower() == 'n':
            return
        index = len([file for file in os.listdir(os.path.join(self.scriptDir, 'autocalibration')) if file.endswith('.json')])
        
        # initial_pinhole_pos = int(self.pinhole)
        # self.close_pinhole(pinhole_size)
        self.close_mono_shutter()
        
        for wl in wavelengths:
            self.go_to_laser_wavelength(wl, autoshutter=True)
            self.go_to_grating_wavelength(wl, autoshutter=True)
            scan_data = self.run_ldr0_scan(motor)
            # Apply the conversion to ensure the data is serializable
            calibrationDict[float(wl)] = scan_data

            print("Saving state...")        

            with open(os.path.join(self.scriptDir, 'autocalibration', 'autocal_{}_{}.json'.format(index, motor)), 'w') as f:
                json.dump(calibrationDict, f)

        print(f"{motor.lower()} Scan complete. Data saved to autocal_{index}_{motor}.json")

        # self.open_pinhole_shutter()
        print("Returning to initial position")
        self.go_to_laser_steps(initial_laser)
        self.go_to_grating_steps(initial_grating)

        # self.open_pinhole(initial_pinhole_pos)
    
    # def close_pinhole(self):
    #     self.
    
    def run_ldr0_scan(self, motor, search_length=None, resolution=None):
        if motor not in ['g1', 'g2', 'l2']:
            print("Invalid motor. Must be 'g1', 'g2', or 'l2'")
            return
        if search_length is None:
            search_length = self.ldr_scan_dict[motor]['range']
        if resolution is None:
            resolution = self.ldr_scan_dict[motor]['resolution']

        # build a dictionary of motor positions
        posDict = {'l1': self.laser_steps[0], 'l2': self.laser_steps[1], 'g1': self.grating_steps[0], 'g2': self.grating_steps[1]}
        current_pos = posDict[motor]
        scan_data = []
        scan_points = np.arange(current_pos - search_length, current_pos + search_length, resolution)

        for idx, final_pos in enumerate(scan_points):
            self.process_coms("{} {}".format(motor, final_pos - current_pos))
            if idx == 0:
                # self.wait_for_motors_manual([final_pos, self.grating_steps[1]], 'B')
                self.wait_for_motors()
            scan_data.append([int(final_pos), 6000-int(self.read_ldr0())])
            current_pos = final_pos
        
        return scan_data

            

        pass

    def print_debug(self):
        print('Entering print debug')
        breakpoint()

    def read_ldr0(self):
        response = self.process_coms('rldr0')
        ldr_value = int(response[0][1:])
        print("LDR0:", ldr_value)
        return ldr_value

    # def shutter_monochromator(self, state):
    #     if state == 'open' or state == 'o':
    #         self.process_coms('gsh off')
    #     elif state == 'close' or state == 'c':
    #         self.process_coms('gsh on')

    def close_mono_shutter(self):
        self.process_coms('gsh on')
    
    def open_mono_shutter(self):
        self.process_coms('gsh off')

    def set_pinhole_pos(self, pos):
        try:
            pos = int(pos)
        except:
            print('Invalid input')
            return
        grating_pos = self.get_grating_motor_positions()
        grating_pos[2] = pos
        self.process_coms('setposb {},{},{},{}'.format(*grating_pos))
        self.pinhole = pos
        print('Pinhole position set to {}'.format(pos))

        # [-1166.0, -1027.0, 0.0, 0.0]

    def move_pinhole(self, z):
        if self.pinhole is None:
            # pinhole = self.get_motor_positions().z
            while True:
                pinhole = input('Enter current pinhole position: ')
                try:
                    # pinhole = int(pinhole)
                    self.pinhole = int(pinhole)
                    break
                except:
                    print('Invalid input')
        
        try:
            z = int(z)
        except:
            print('Invalid input')
            return
        if z < 0 or z > 160:
            print('Invalid input - must be between 0 and 160')
            return
        move_motor = z - self.pinhole
        self.process_coms('z {}'.format(move_motor))
        self.wait_for_motors()
        self.pinhole = z

    def unlock_calibration(self):
        '''Unlocks the calibration so that G1 and G2 can be moved independently.'''
        self.calibrations.__setattr__('wl_to_g2', np.poly1d(self.all_calibrations['wl_to_g2_subtractive']))
        print('Calibration unlocked. G2 is now independent of G1.')

    def lock_calibration(self):
        '''Takes the current monochromator positions and makes G2 a function of G1 at this position. Only works for subtractive operation mode. Note the g2_to_wl calibration is still the original, so the calculated wavelength may be innacurate, but the position will be correct.'''

        motor_positions = self.get_grating_motor_positions() # FIX - make this a .get() function of an attribute
        g2_pos = motor_positions[1]
        g2_calibration = [x for x in self.all_calibrations['wl_to_g1_subtractive']]
        g2_calibration[2] += g2_pos
        self.calibrations.__setattr__('wl_to_g2_subtractive', np.poly1d(g2_calibration))
        # breakpoint()
        print('Calibration locked. G2 is now a function of G1 at this position.')

    def ammend_calibrations(self, report=True):
        '''If an autocalibration has been performed, this function will update the current calibrations with the new data. Loads individual files'''
        json_files = [f for f in os.listdir(self.calibrationDir) if f.endswith('autocal.json')]


        if len(json_files) == 0:
            print('No autocalibration data found.')
            return
        
        report_dict = {}

        for file in json_files:

            with open(os.path.join(self.calibrationDir, file), 'r') as f:
                data = json.load(f)

            for name, calib in data.items():
                # print("Updating {} with autocalibration data".format(name))
                if len(calib) == 7:
                    # print("Loading {} as poly_sin".format(name))
                    report_dict[name] ='poly_sin'
                    self.calibrations.__setattr__(name, PolySinModulation(*calib))
                elif len(calib) == 6:
                    # print("Loading {} as lin_sin".format(name))
                    report_dict[name] = 'lin_sin'
                    self.calibrations.__setattr__(name, LinSinModulation(*calib))
                else:
                    # print("Loading {} as poly1d".format(name))
                    report_dict[name] = 'poly1d'
                    self.calibrations.__setattr__(name, np.poly1d(calib))

        if report:
            for key, value in report_dict.items():
                print(f'{key} updated as {value}')
        print('Calibrations updated with autocalibration data')
        print('-'*20)


    def __generate_calibrations(self, report=False):
        self.calibrationDir = os.path.join(self.scriptDir, 'calibrations')

        with open(os.path.join(self.calibrationDir, 'calibrations_main.json'), 'r') as f:
            calibrations = json.load(f)
            print('Calibrations loaded from file')
        
        self.all_calibrations = calibrations
        self.calibrations = SimpleNamespace()
        
        for name, calib in calibrations.items():
            if len(calib) == 7:
                print("Loading {} as poly_sin".format(name))
                self.calibrations.__setattr__(name, PolySinModulation(*calib))
            if len(calib) == 6:
                print("Loading {} as poly_sin".format(name))
                self.calibrations.__setattr__(name, LinSinModulation(*calib))
            else:
                print("Loading {} as poly1d".format(name))
                self.calibrations.__setattr__(name, np.poly1d(calib))

        print("defaulting to additive calibration for G1. Return to fix this later.")
        self.calibrations.g1_to_wl = self.calibrations.g1_to_wl_additive
        self.calibrations.wl_to_g1 = self.calibrations.wl_to_g1_additive

        print("Calibrations successfully built.")

        #save peanut -45
        # self.calibrations = SimpleNamespace(**self.calibrations)
        # self.calibrations = SimpleNamespace(**{calib: np.poly1d(calibrations[calib]) for calib in calibrations})

    def show_help(self):
        print('Available commands:')
        for key in self.microscope_functions:
            print(key)

    def guess_mode(self):
        current_grating_pos = self.get_grating_motor_positions()
        if current_grating_pos[1] < -3000:
            self.monochromator_mode = 'additive'
            print('Guessed additive mode')
            self._switch_calibrations('additive', overwrite=True)
        else:
            self.monochromator_mode = 'subtractive'
            print('Guessed subtractive mode')
            self._switch_calibrations('subtractive', overwrite=True)

    def _switch_calibrations(self, mode, overwrite=False):
        if mode == 'additive':
            # self.calibrations = SimpleNamespace(**{calib: np.poly1d(self.calibration_backup[calib]) for calib in self.calibration_backup})
            self.calibrations.wl_to_g2 = self.calibrations.wl_to_g2_additive
            self.calibrations.g2_to_wl = self.calibrations.g2_to_wl_additive
        elif mode == 'subtractive':
            # self.calibrations = SimpleNamespace(**{calib: np.poly1d(self.calibration_backup[calib]) for calib in self.calibration_backup})
            self.calibrations.wl_to_g2 = self.calibrations.wl_to_g2_subtractive
            self.calibrations.g2_to_wl = self.calibrations.g2_to_wl_subtractive

    #g2 start -39
    def change_monochromator_mode(self, mode):
        if mode == self.monochromator_mode:
            print('Already in mode {}'.format(mode))
            ovr = input('Override? (y/n)')

            if ovr == 'n':
                return
        if mode == 'additive':
            self._switch_calibrations('additive')
            self.monochromator_mode = 'additive'
            print('Switched to additive mode')
        elif mode == 'subtractive':
            self._switch_calibrations('subtractive')
            self.monochromator_mode = 'subtractive'
            print('Switched to subtractive mode')
        

    
            # self.to_addivite = -12990


    def report_status(self):
        if self.triax_steps is None:
            dummy_triax = 407225
            self.triax_steps = dummy_triax
        else:
            self.triax_steps = self.get_triax_steps()
        self.laser_steps = self.get_laser_motor_positions()
        self.grating_steps = self.get_grating_motor_positions()

        report = {
            'monochromator mode': self.monochromator_mode,
            'laser l1, l2 lambda': self.calculate_laser_wavelength(self.laser_steps),
            'g1 lambda': self.calculate_grating_wavelength(self.grating_steps),
            'TRIAX lambda': self.calculate_triax_wavelength(self.triax_steps),
            'laser motor positions': self.laser_steps,
            'grating motor positions': self.grating_steps,
            'laser wavenumber': self.current_laser_wavenumber,
            'grating wavenumber': self.current_grating_wavenumber,
            # 'Raman wavelength': self.current_raman_wavelength,
            'Raman shift': self.current_shift,
            # 'pinhole': self.pinhole
        }

        if  report['g1 lambda'][0] < 500 or report['g1 lambda'][0] > 2000:
            print('Grating wavelength out of range - please check monochromator mode')

        self.pinhole = report['grating motor positions'][2]
        report['pinhole'] = self.pinhole

        print('-'*20)
        for key, value in report.items():
            print('{}: {}'.format(key, value))
        print('-'*20)

    def calculate_triax_position(self):
        ''''''

    def get_grating_wavelength(self):
        return 

    @property
    def current_grating_wavelength(self):
        return self.calculate_grating_wavelength()

    @property
    def current_laser_wavelength(self):
        return self.calculate_laser_wavelength()
    
    @property
    def current_laser_wavenumber(self):
        '''Takes the current laser wavelength and calculates the absolute wavenumbers.'''
        return 10_000_000/self.laser_wavelength[0]
    
    # def calculate_relative_shift(self, delta_lambda):
    #     '''Calculates the '''
         
    # @property
    # def current_raman_wavelength(self):
    #     '''Calculates the current wavelength that corresponds to the current Raman shift at this excitation wavelength.'''
    #     return 10_000_000/self.current_grating_wavenumber

    def calculate_raman_shift_wavelength(self, raman_shift):
        '''Calculates the wavelength in nm that corresponds to the given raman shift at the current laser wavelength.'''
        wavenumbers = self.current_laser_wavenumber - raman_shift
        return 10_000_000/wavenumbers

    
    @property
    def current_grating_wavenumber(self):
        '''Takes the current laser wavenumber and calculates the absolute wavenumber for the current raman shift.'''
        return 10_000_000/self.current_grating_wavelength[0]
    
    def wavenumber_to_wavelength(self, wavenumber):
        return 10_000_000/wavenumber
    
    def wavelength_to_wavenumber(self, wavelength):
        return self.wavenumber_to_wavelength(wavelength)

    def simple_calibration_shift(self, raman_shift=None):
        '''Takes the current motor positions as the new position for the current wavelength. Simply sets the motor steps to the calcualted position for the current wavelength.'''

        if raman_shift is not None:
            self.current_shift = float(raman_shift)

        # breakpoint()
        
        current_laser_pos = self.get_laser_motor_positions()
        current_laser_wavelength, l2_wavelength = self.calculate_laser_wavelength(current_laser_pos)
        current_grating_pos = self.get_grating_motor_positions()
        current_grating_wavenumber = self.current_grating_wavenumber
        # What the current wavelength should be at the detector
        current_detector_wavelength = self.wavenumber_to_wavelength(current_grating_wavenumber)
        print(current_detector_wavelength)
# Write function to store Raman shift on microcontrollers and get it back.


        # calculate the motor positions which correspond to the current wavelength
        l1_target = round(self.calibrations.wl_to_l1(current_laser_wavelength))
        l2_target = round(self.calibrations.wl_to_l2(current_laser_wavelength))
        g1_target = round(self.calibrations.wl_to_g1(current_detector_wavelength))
        g2_target = round(self.calibrations.wl_to_g2(current_detector_wavelength))

        print('Current Positions:\n Laser: {}\n Grating: {}'.format(current_laser_pos, current_grating_pos))
        print('Target Positions:\n Laser: {}\n Grating: {}'.format([l1_target, l2_target], [g1_target, g2_target]))

        # set the motor positions to the calculated positions, shifting the calibration to the current wavelength
        self.set_absolute_positions_A(f'{l1_target},{l2_target},0,0')
        self.set_absolute_positions_B(f'{g1_target},{g2_target},{self.pinhole},0')
        
        new_laser_pos = self.get_laser_motor_positions()
        new_laser_wavelength, l2_wavelength = self.calculate_laser_wavelength(new_laser_pos)
        new_grating_pos = self.get_grating_motor_positions()
        new_grating_wavelength = self.calculate_grating_wavelength(new_grating_pos)[0]
        
        if new_grating_pos[0] == g1_target and new_grating_pos[1] == g2_target and new_laser_pos[0] == l1_target and new_laser_pos[1] == l2_target:
            print('Calibration shift successful')
            print('New Positions:\n Laser: {}\n Grating: {}'.format(new_laser_wavelength, new_grating_wavelength))
        else:
            print('Calibration shift failed')
            print('New Positions:\n Laser: {}\n Grating: {}'.format(new_laser_wavelength, new_grating_wavelength))


    def extract_coms_message(self, message):
        return message[1].split(':')[1].strip(' ')

    def wait_for_motors(self, delay=0.1):
        '''Waits for the motors to finish moving by polling the motors until they are no longer running.'''
        count = 0
        running_A = True
        running_B = True
        while running_A is True or running_B is True:

            if running_A is True:
                response = self.process_coms('Aisrun')
                # res = response[0].split(':')[0]
                res1 = self.extract_coms_message(response)
                # 
                if res1 == 'S0':
                    running_A = False
                # elif res1 == 'R1':
                else:
                    print("A running")
                    time.sleep(delay)
                    continue

            if running_B is True:
                response = self.process_coms('Bisrun')
                res2 = self.extract_coms_message(response)
                if res2 == 'S0':
                    running_B = False
                # elif res2 == 'R1':
                else:
                    time.sleep(delay)
                    print("B running")
                    continue
                
            if count > 0:
                print("Loop broke")
                
            count += 1

        return 'S0'
    
    def wait_for_motors_manual(self, targets, motors):
        motor_dict = {
            'A': self.get_laser_motor_positions,
            'B': self.get_grating_motor_positions,
            # Add more motors here as needed
        }



        get_positions = motor_dict.get(motors)
        if get_positions is None:
            raise ValueError(f"Unexpected motor identifier: {motors}")

        while True:
            positions = get_positions()
            if positions[0] == targets[0] and positions[1] == targets[1] and positions[2] == targets[2] and positions[3] == targets[3]:
                break
            time.sleep(0.2)

        # self.current_motor_positions[motors] = positions

        print('Motors at target positions')
    
        # 

    def confirm_motor_positions(self, targets, motors):
        motor_dict = {
            'A': self.get_laser_motor_positions,
            'B': self.get_grating_motor_positions,
            # Add more motors here as needed
        }

        get_positions = motor_dict.get(motors)
        if get_positions is None:
            raise ValueError(f"Unexpected motor identifier: {motors}")

        positions = get_positions()
        if positions[0] == targets[0] and positions[1] == targets[1] and positions[2] == targets[2] and positions[3] == targets[3]:
            print("Motors at target positions")
            return True
        else:
            print("ERROR: Motors not at target positions")
            return False

    def get_all_current_positions(self):
        l1_wavelength, l2_wavelength = [round(x, 2) for x in self.calculate_laser_wavelength()]


        b_positions = self.calculate_grating_wavelength()
        g1_wavelength = round(b_positions[0], 2)
        g2_wavelength = round(b_positions[1], 2)
        # pin_pos = b_positions[2]
        g2_pos = self.get_grating_motor_positions()
        l1_pos = self.get_laser_motor_positions()
        try:
            triax_pos = self.get_triax_steps()
            triax_wavelength = self.calculate_triax_wavelength(steps=triax_pos)
        except Exception as e:
            print('Error getting triax position')
            print(e)
            triax_pos = 0
            triax_wavelength = 0

        
        print('laser pos: {}'.format(l1_pos))
        print('grating pos: {}'.format(g2_pos))
        print('triax pos: {}'.format(triax_pos))

        print('triax wavelength: {}'.format(triax_wavelength))
        print('l1 wavelength: {}'.format(l1_wavelength))
        print('l2 wavelength: {}'.format(l2_wavelength))
        print('g1 wavelength: {}'.format(g1_wavelength))
        print('g2 wavelength: {}'.format(g2_wavelength))
        # print('Current pinhole position: {}'.format(pin_pos))

        # TODO: Change to @property


        return 
        
    def get_laser_motor_positions(self):
        # print('entered get laser')
        try:
            response = self.process_coms('gpa')
            print('got response')
            positions = response[1].split(':')[1]
            positions = positions.strip('<P>P')
            positions = positions.split(',')
            self.laser_steps = [float(x[1:]) for x in positions]
        except Exception as e:
            traceback.print_exc()
            print('Error getting laser position')
            print(e)
            return
        
        print('Current laser pos: {}'.format(self.laser_steps))
        return self.laser_steps
    
    def get_grating_motor_positions(self):
        try:
            response = self.process_coms('gpb')
            positions = response[1].split(':')[1]
            positions = positions.strip('<P>P')
            positions = positions.split(',')
            self.grating_steps = [float(x[1:]) for x in positions]
        except Exception as e:
            traceback.print_exc()
            print('Error getting grating position')
            print(e)
            return
        
        print('Current grating pos: {}'.format(self.grating_steps))
        return self.grating_steps
    
    def calculate_laser_wavelength(self, current_pos=None):
        if current_pos is None:
            current_laser_pos = self.get_laser_motor_positions()
        else:
            current_laser_pos = current_pos

        self.laser_steps = current_laser_pos

        l1_pos = current_laser_pos[0]
        l2_pos = current_laser_pos[1]

        l1_wavelength = self.calibrations.l1_to_wl(l1_pos)
        l2_wavelength = self.calibrations.l2_to_wl(l2_pos)

        self.laser_wavelength = [l1_wavelength, l2_wavelength, 0, 0]
        
        # print('Current laser wavelength: {}'.format(l1_wavelength))
        return l1_wavelength, l2_wavelength
    
    def calculate_grating_wavelength(self, current_pos=None):
        if current_pos is None:
            current_grating_pos = self.get_grating_motor_positions()
        else:
            current_grating_pos = current_pos

        g1_pos = current_grating_pos[0]
        g2_pos = current_grating_pos[1]
        pin_pos = current_grating_pos[2]

        self.grating_steps = current_grating_pos

        # if self.monochromator_mode == 'additive':
        #     g2_pos = g2_pos - self.to_addivite

        g1_wavelength = self.calibrations.g1_to_wl(g1_pos)
        g2_wavelength = self.calibrations.g2_to_wl(g2_pos)

        self.grating_wavelength = [g1_wavelength, g2_wavelength, pin_pos, 0]

        return (g1_wavelength, g2_wavelength, pin_pos)

    def go_to_wavenumber(self, wavenumber):
        try:
            wavenumber = float(wavenumber)
        except ValueError:
            print('Invalid value for wavenumber - use a number')
            return
        if self.laser_wavelength is None:
            self.get_all_current_positions()
        
        # ;
        laser_wavenumber = self.current_laser_wavenumber
        # 
        wave = laser_wavenumber - wavenumber
        new_wavelength = 10_000_000/wave
        self.go_to_grating_wavelength(new_wavelength)
        self.current_shift = wavenumber
        print('Moving to wavenumber: {} for {} nm excitation'.format(wavenumber, self.laser_wavelength[0]))

    def go_to_laser_wavelength(self, wavelength, autoshutter=True):
        '''Currently operating as movements in relative mode. Add feature in the future to move in absolute mode.
        Uses the calibrations to move the laser motors into position for a specified wavelength.'''
        # 
        if autoshutter is True:
            # every time the laser moves the shutter should close. A final check for light on the LDR should be added before opening the shutter to minimise chances of laser damage on detector #TODO: Add this check
            self.close_mono_shutter()

        try:
            wavelength = float(wavelength)
        except ValueError:
            print('Invalid value for wavelength - use a number')
            return
        
        if not 650 < wavelength < 1000:
            print('Wavelength out of range. Pick a wavelength between 650 and 1000 nm')
            return

        current_pos = self.get_laser_motor_positions()
        if current_pos is None:
            return 

        l1_target = round(self.calibrations.wl_to_l1(wavelength))
        # print("l1 target: {}".format(l1_target))

        l2_target = round(self.calibrations.wl_to_l2(wavelength))
        # print("l2 target: {}".format(l2_target))
        print('Current laser position: {}'.format(current_pos))
        print('Target laser position: {}'.format([l1_target, l2_target]))
        move_l1 = l1_target - current_pos[0]
        move_l2 = l2_target - current_pos[1]
        print("moving l1 by {}".format(move_l1))

        backlash = False
        # self.move_to(target_pos)
        if move_l1 != 0:
            if move_l1 < 0:
                backlash = True
            response = self.process_coms('l1 {}'.format(move_l1))

        if move_l2 != 0:
            if move_l2 < 0:
                backlash = True
            response = self.process_coms('l2 {}'.format(move_l2))

        # self.wait_for_motors_manual([l1_target, l2_target, 0, 0], 'A')
        self.wait_for_motors()

        if backlash:
            response = self.process_coms('l1 -20')
            response = self.process_coms('l2 -20')
            time.sleep(0.1)
            response = self.process_coms('l1 20')
            response = self.process_coms('l2 20')

        self.confirm_motor_positions([l1_target, l2_target, 0, 0], 'A')
        self.laser_steps[0] = l1_target
        self.laser_steps[1] = l2_target

        print('Laser excitation at {}'.format(wavelength))
        if autoshutter is True:
            self.laser_safety_check()
            # self.open_pinhole_shutter() # add check that light levels are safe #TODO: Add this check
            self.open_mono_shutter()

        self.calculate_laser_wavelength(self.laser_steps)

    def close_pinhole(self, pos=0):
        self.save_pinhole = int(self.pinhole) # backs up last position
        # response = self.process_coms('pin {}'.format(pos))
        self.move_pinhole(pos)
        self.wait_for_motors()
        print('Pinhole at {}'.format(pos))

    def open_pinhole(self, pos=160):
        self.save_pinhole = int(self.pinhole) # backs up last position
        # response = self.process_coms('pin {}'.format(pos))
        self.move_pinhole(pos)
        self.wait_for_motors()

        # breakpoint()
        print('Pinhole opened at {}'.format(pos))


    def go_to_laser_steps(self, laser_pos:list):
        '''Moves the laser motors to the specified position in steps.'''
        current_pos = self.get_laser_motor_positions()
        if current_pos is None:
            return 

        l1_target = laser_pos[0]
        l2_target = laser_pos[1]
        move_l1 = l1_target - current_pos[0]
        move_l2 = l2_target - current_pos[1]

        backlash = False
        if move_l1 != 0:
            if move_l1 < 0:
                backlash = True
            response = self.process_coms('l1 {}'.format(move_l1))

        if move_l2 != 0:
            if move_l2 < 0:
                backlash = True
            response = self.process_coms('l2 {}'.format(move_l2))

        # self.wait_for_motors_manual([l1_target, l2_target, 0, 0], 'A')
        self.wait_for_motors()

        if backlash:
            response = self.process_coms('l1 -20')
            response = self.process_coms('l2 -20')
            time.sleep(0.1)
            response = self.process_coms('l1 20')
            response = self.process_coms('l2 20')


        self.confirm_motor_positions([l1_target, l2_target, 0, 0], 'A')
        self.laser_steps = laser_pos

        print('Laser motors moved to position {}'.format(laser_pos))

    def go_to_grating_steps(self, grating_pos:list):
        '''Moves the grating motors to the specified position in steps.'''

        current_pos = self.get_grating_motor_positions()
        if current_pos is None:
            return 

        # g1_target = round(self.calibrations.wl_to_g1(wavelength))
        # print("l1 target: {}".format(g1_target))

        # g2_target = round(self.calibrations.wl_to_g2(wavelength))
        g1_target = grating_pos[0]
        g2_target = grating_pos[1]
        pinhole_target = grating_pos[2]
        # print("l2 target: {}".format(g2_target))
        move_g1 = g1_target - current_pos[0]
        move_g2 = g2_target - current_pos[1] # 1, 13, 0, 0/ -21, -11, 0, 0
        move_pinhole = pinhole_target - current_pos[2]

        backlash = False
        if move_g1 != 0:
            if move_g1 < 0:
                backlash = True
                # move_g1 = move_g1 - 20 # move 20 steps further to correct for backlash
            response = self.process_coms('g1 {}'.format(move_g1))

        if move_g2 != 0:
            if move_g2 < 0:
                backlash = True
                # move_g2 = move_g2 - 20 # move 20 steps further to correct for backlash
            response = self.process_coms('g2 {}'.format(move_g2))

        if move_pinhole != 0:
            response = self.process_coms('z {}'.format(move_pinhole))

        # self.wait_for_motors_manual([g1_target, g2_target, pinhole_target, 0], 'B')
        self.wait_for_motors()
        # time.sleep(5)
        if backlash:
            response = self.process_coms('g1 -20')
            response = self.process_coms('g2 -20')
            time.sleep(0.1)
            response = self.process_coms('g1 20')
            response = self.process_coms('g2 20')


        self.confirm_motor_positions([g1_target, g2_target, pinhole_target, 0], 'B')
        self.grating_steps = grating_pos

        print('Grating motors moved to position {}'.format(grating_pos))

    def laser_safety_check(self, limit=20):
        '''If the detector wavelength is within 20 wavenumbers of the laser wavelength, warn the user and prompt to overwrite or revert to a safe position.'''

        # grating_wavelength = self.calculate_grating_wavelength()[0]
        if self.detector_safety is False:
            return
        
        if self.current_laser_wavenumber + limit > self.current_grating_wavenumber > self.current_laser_wavenumber - limit:
            print(f'Warning: Detection is within {limit} wavenumbers of the laser wavelength - press enter to revert to safety')
            command = input()
            if command == 'overwrite':
                return
            else:
                print('Moving to raman shift of 200 cm-1')
                self.current_shift = 200
                self.go_to_wavenumber(self.current_shift)

    def go_to_grating_wavelength(self, wavelength, step=None, autoshutter=True):
        '''Currently operating as movements in relative mode. Add feature in the future to move in absolute mode.'''

        if autoshutter is True:
            # self.close_pinhole_shutter() # every time the laser moves the shutter should close. A final check for light on the LDR should be added before opening the shutter to minimise chances of laser damage on detector #TODO: Add this check
            self.close_mono_shutter()

        try:
            wavelength = float(wavelength)
        except ValueError:
            print('Invalid value for wavelength - use a number')
            return
        
        if not 600 < wavelength < 1200:
            print('Wavelength out of range. Pick a wavelength between 600 and 1200 nm')
            return

        current_pos = self.get_grating_motor_positions()
        if current_pos is None:
            return 

        g1_target = round(self.calibrations.wl_to_g1(wavelength))
        # print("l1 target: {}".format(g1_target))

        g2_target = round(self.calibrations.wl_to_g2(wavelength))
        # print("l2 target: {}".format(g2_target))
        move_g1 = g1_target - current_pos[0]
        move_g2 = g2_target - current_pos[1] # 1, 13, 0, 0/ -21, -11, 0, 0

        
        # if self.monochromator_mode == 'additive':
        #     move_g2 = g2_pos - self.to_addivite


        # self.move_to(target_pos)
        backlash = False
        if move_g1 != 0:
            if move_g1 < 0:
                backlash = True
                # move_g1 = move_g1 - 20 # move 20 steps further to correct for backlash
            response = self.process_coms('g1 {}'.format(move_g1))

        if move_g2 != 0:
            if move_g2 < 0:
                backlash = True
                # move_g2 = move_g2 - 20 # move 20 steps further to correct for backlash
            response = self.process_coms('g2 {}'.format(move_g2))

        # self.wait_for_motors_manual([g1_target, g2_target, 0, 0], 'B')
        self.wait_for_motors()
        # time.sleep(5)
        if backlash:
            response = self.process_coms('g1 -20')
            response = self.process_coms('g2 -20')
            time.sleep(0.1)
            response = self.process_coms('g1 20')
            response = self.process_coms('g2 20')

        self.confirm_motor_positions([g1_target, g2_target, 0, 0], 'B')
        self.grating_steps[0] = g1_target
        self.grating_steps[1] = g2_target

        print('Grating detection at {}'.format(wavelength))
        # self.current_grating_positions = [g1_target, g2_target]

        if autoshutter is True:
            # self.open_pinhole_shutter() # add check that light levels are safe #TODO: Add this check
            self.laser_safety_check()
            self.open_mono_shutter()

        self.calculate_grating_wavelength(self.grating_steps)
            



    def reference_calibration(self, steps=None):
        '''Used to reference the current motor position to the laser wavelength, as defined by the current calibration. Measure a spectrum on the TRIAX and enter the stepper motor position and pixel count of the peak wavelength here. In the future, this will be automated with a peak detection algorithm.'''
        # Instructions: Ensure that the entire system is well aligned, and that the stepper motors are in the correct positions relative to one another for passing the laser wavelength to the spectrograph.
        # Centre the laser peak in pixel 50 of the CCD. Enter the stepper motor position here.
        if steps is None:
            steps = self.get_triax_steps()
        true_wavelength = self.calibrations.triax_steps_to_wl(float(steps))
        print('True wavelength: {}. Shifting motor positions to true wavelength'.format(true_wavelength))
        
        
        l1_target = round(self.calibrations.wl_to_l1(true_wavelength))
        l2_target = round(self.calibrations.wl_to_l2(true_wavelength))
        g1_target = round(self.calibrations.wl_to_g1(true_wavelength))
        g2_target = round(self.calibrations.wl_to_g2(true_wavelength))

        # breakpoint() #378617

        self.set_absolute_positions_A(f'{l1_target},{l2_target},0,0')
        self.set_absolute_positions_B(f'{g1_target},{g2_target},{self.pinhole},0')

        laser_pos = self.get_laser_motor_positions()
        grating_pos = self.get_grating_motor_positions()

        if l1_target == laser_pos[0] and l2_target == laser_pos[1]:
            print('Laser motors successfully calibrated')
        else:
            print('Error calibrating laser motors')
            print('Expected: {}, {}'.format(l1_target, l2_target))
            print('Actual: {}, {}'.format(laser_pos[0], laser_pos[1]))
        
        if g1_target == grating_pos[0] and g2_target == grating_pos[1]:
            print('Grating motors successfully calibrated')
        else:
            print('Error calibrating grating motors')
            print('Expected: {}, {}'.format(g1_target, g2_target))
            print('Actual: {}, {}'.format(grating_pos[0], grating_pos[1]))


    def set_absolute_positions_A(self, positions):
        # command = 'o{}o'.format(self.tuning_motor_dict['setposA'], positions)
        print("Setting absolute positions A: {}".format(positions))
        response = self.process_coms('setposA {}'.format(positions))
    
    def set_absolute_positions_B(self, positions):
        print("Setting absolute positions B: {}".format(positions))
        # command = 'o{}o'.format(self.tuning_motor_dict['setposA'], positions)
        response = self.process_coms('setposB {}'.format(positions))


    def set_acquisition_time(self, acq_time):
        try:
            self.acq_time = float(acq_time)
        except ValueError:
            print('Invalid value for acquisition time')
        print('Acquisition Time Set: {}'.format(self.acq_time))

    def process_coms(self, coms: str):
        response = None

        com = [item.lower() for item in coms.split(' ')]

        if com[0] == 'eept':
            command = 'o{}o'.format(self.tuning_motor_dict['gpa'])
            if len(com) > 1:
                extra = ','.join(com[1:])
            else:
                extra = ''
            # print('UI>UNO:{}'.format(command))
            self.send_command_to_UNO(command)
            time.sleep(0.1)
            # 
            response = self.read_from_serial_until()
            # print(response)
            # 
            gpa = response[1].split('<P')[1]
            gpa = gpa.split('P>')[0]
            gpa = gpa.split(',')

            command = 'o{}o'.format(self.tuning_motor_dict['gpb'])
            # print('UI>UNO:{}'.format(command))
            self.send_command_to_UNO(command)
            time.sleep(0.1)
            # 
            response = self.read_from_serial_until()
            # print(response)
            gpb = response[1].split('<P')[1]
            gpb = gpb.split('P>')[0]
            gpb = gpb.split(',')

            
            with open(os.path.join(self.scriptDir, 'eept.txt'), 'a') as f:
                f.write('{}:{}:{}\n'.format(gpa, gpb, extra))
            print(f'exporting {gpa}:{gpb}:{extra}')
            return (f'exporting {gpa}:{gpb}')
            
            # sulfur REF: 210 sd (220 peak)
        
        # REF: 900 pixels (~ 1 window) ~= 250 cm-1 ~= 13 nm

        if com[0] == 'aapt': # puts the current positions of the motors into a file. Uses laser l1 calibration for the wavelength axis, and uses the raman shift applied to the (l1) calculated laser energy to provide a reference for the grating calibrations.
            command = 'o{}o'.format(self.tuning_motor_dict['gpa'])
            if len(com) > 1:
                extra = ','.join(com[1:])
            else:
                extra = ''
            # print('UI>UNO:{}'.format(command))
            self.send_command_to_UNO(command)
            time.sleep(0.1)
            # 
            response = self.read_from_serial_until()
            # print(response)
            # 
            gpa = response[1].split('<P')[1]
            gpa = gpa.split('P>')[0]
            gpa = gpa.split(',')

            command = 'o{}o'.format(self.tuning_motor_dict['gpb'])
            # print('UI>UNO:{}'.format(command))
            self.send_command_to_UNO(command)
            time.sleep(0.1)
            # 
            response = self.read_from_serial_until()
            # print(response)
            gpb = response[1].split('<P')[1]
            gpb = gpb.split('P>')[0]
            gpb = gpb.split(',')

            laser_wavelength, l2_wavelength = self.calculate_laser_wavelength()
            grating_wavelength = self.grating_wavelength[0]

            
            with open(os.path.join(self.scriptDir, 'aapt.txt'), 'a') as f:
                f.write('{}:{}:{}:{}\n'.format(laser_wavelength, gpa, gpb, grating_wavelength))
            print(f'exporting {laser_wavelength}:{gpa}:{gpb}:{grating_wavelength}')
            return (f'exporting {laser_wavelength}:{gpa}:{gpb}:{grating_wavelength}')
            



        if com[0] in self.general_dict.keys():
            self.general_dict[com[0]]()
            response = 'Connected to {}'.format(com[0])

        elif com[0] in self.acquisition_dict.keys():
            if len(com) > 1:
                command = 'm{}{}m'.format(self.acquisition_dict[com[0]], com[1])
            else:
                command = 'm{}m'.format(self.acquisition_dict[com[0]])
            print('UI>UNO:{}'.format(command))
            self.send_command_to_UNO(command)
            time.sleep(0.1)
            response = self.read_from_serial_until()
            return response


        elif com[0] in self.tuning_motor_dict.keys():
            # print('entered turning dict')
            if len(com) > 1:
                command = 'o{}{}o'.format(self.tuning_motor_dict[com[0]], com[1])
            else:
                command = 'o{}o'.format(self.tuning_motor_dict[com[0]])
            print('UI>UNO:{}'.format(command))
            self.send_command_to_UNO(command)
            time.sleep(0.1)
            # 
            response = self.read_from_serial_until()
            # print(response)
            return response
            # 
        
        elif com[0] in self.laser_dict.keys():

            command = self.laser_dict[com[0]]
            self.send_command_to_laser(command)
            time.sleep(0.01)
            # response = self.laser_serial.read(self.laser_serial.inWaiting())
            response = self.read_from_laser()
            print(response)
            return response
            # 

        elif com[0] in self.microscope_functions.keys():
            if len(com) > 1:
                response = self.microscope_functions[com[0]](*com[1:])
            else:
                response = self.microscope_functions[com[0]]()

            return response


        elif com[0] in self.spectrometer_dict.keys():
            if len(com) > 1:
                command = '{} {}'.format(self.spectrometer_dict[com[0]], com[1])
            else:
                command = self.spectrometer_dict[com[0]]

            response = self.send_command_to_spectrometer(command)
            return response
        
        elif com[0] in self.stage_dict.keys():
            pass # palceholder for stage control
            return response


        else:
            print('Command not recognized: {}'.format(com))

        return response


    

    def connect_to_laser(self, laserCom='COM12'):
        self.laser_serial = serial.Serial(laserCom, 9600, timeout=1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, xonxoff=False, rtscts=False, dsrdtr=False)
        return self.laser_serial
    
    def send_command_to_laser(self, command):
        initial_response = self.laser_serial.write('{}\r'.format(command).encode())
        # time.sleep(0.01)

    def read_from_laser(self):
        response = self.laser_serial.read(self.laser_serial.inWaiting())
        return response
        # response = self.laser_serial.readline()
        response = ''
        while self.laser_serial.in_waiting > 0: #FIX: Change the logic to do this in the main loop
            # print(response)
            response += self.laser_serial.readline().decode()
        # response = self.uno_serial.read(self.uno_serial.inWaiting()).decode().strip('\r\n')
        # print('Finihsed reading command from uno: {}'.format(response))
        return response
        # print(response)
        # 

    def connect_to_UNO(self, unoCOM='COM8', baud=9600):
        UNO_serial = serial.Serial(unoCOM, baud, timeout=1)
        while UNO_serial.in_waiting == 0:
            time.sleep(0.1)
        while UNO_serial.in_waiting > 0:
            response = UNO_serial.readline().decode().strip()
            print(response)
        return UNO_serial
    
    def send_command_to_UNO(self, command):
        self.uno_serial.write('{}\n'.format(command).encode())
        # print('finisehd sending to uno')
        time.sleep(0.1)
        # response = self.uno_serial.read(self.uno_serial.inWaiting())
        # print(response)

    def read_command_from_uno(self):
        # print('reading command from uno')
        response = ''
        while self.uno_serial.in_waiting > 0: #FIX: Change the logic to do this in the main loop
            # print(response)
            response += self.uno_serial.readline().decode()
        # response = self.uno_serial.read(self.uno_serial.inWaiting()).decode().strip('\r\n')
        # print('Finihsed reading command from uno: {}'.format(response))
        return response

    def set_scan_min(self, value):
        try:
            self.scan_min = int(value)
        except ValueError:
            print('Invalid value for scan min')
        print('Scan Min: {}'.format(self.scan_min))

    def set_scan_max(self, value):
        try:
            self.scan_max = int(value)
        except ValueError:
            print('Invalid value for scan max')
        print('Scan Max: {}'.format(self.scan_max))
    
    def set_scan_resolution(self, value):
        try:
            self.scan_resolution = int(value)
        except ValueError:
            print('Invalid value for scan resolution')
        print('Scan Resolution: {}'.format(self.scan_resolution))


    def read_from_serial_until(self, end_flag='#CF', report=False):
        end_responses = []
        while True:
            response = self.read_command_from_uno()
            if response == '':
                time.sleep(0.01)
                continue
            if report:
                print(response)
            split_responses = response.split('\r\n')
            for item in split_responses:
                if item == end_flag:
                    return end_responses
                if item != '':
                    end_responses.append(item)
                    print(item)
            time.sleep(0.01)
            # else:

    def extract_data(self, response):
        if type(response) == float: # TODO: change this to detect data type better
            return response
        new_data = []
        if isinstance(response, int):
            return response
        for item in response:
            if item.startswith("COUNTS:"):
                try:
                    value = item[item.index(':')+2:item.index('/')]
                    timestamp = item[item.index('/')+1:]
                    new_data = [float(value), float(timestamp)]
                except Exception as e:
                    traceback.print_exc()
                    print('Error processing data')
                    print(e)
        return new_data

    def get_grating_position(self):
        response = self.send_command_to_spectrometer('H0')
        response = response.strip()
        grating_pos = int(response[1:])
        self.trax_grating = grating_pos
        print('Grating Pos: {}'.format(response))
        return grating_pos


    def motor_scan(self, motor = 'g2'):
        # Create figure for plotting
        fig, ax = plt.subplots()
        xs = []  # List to store x-axis values (time steps)
        ys = []  # List to store y-axis values (data points)

        # Initialize plot
        line, = ax.plot(xs, ys, 'r-')  # 'r-' means red line
        ax.set_xlim(0, 10)  # Set initial x-axis limits
        ax.set_ylim(0, 1)  # Set initial y-axis limits

        # Display the plot
        plt.ion()
        plt.show()

        def add_data_point(newData):
            # Append new data points to the lists
            xs.append(float(newData[0]))
            ys.append(float(newData[1]))
            
            # Update line data
            line.set_data(xs, ys)
            
            # Adjust x-axis and y-axis limits dynamically
            ax.set_xlim(min(xs), max(xs))
            ax.set_ylim(min(ys) - 0.1, max(ys) + 0.1)
            
            # Redraw the plot
            plt.draw()
            plt.pause(0.01)

        # TODO: Eventually replace code to skip process_coms and call send_to_UNO


        print("custom scan")
        scan_results = np.empty((0, 3)).astype(float)
        grating_pos = self.get_grating_motor_positions()
        grating_wavelength = self.calculate_grating_wavelength(grating_pos)[0]
        scan_min = -100
        scan_max = 100
        scan_resolution = 5
        acq_time = 0.2


        while True:
            print('-'*50)
            print('Perparing wavelength scan. Current Parameters:')
            print('0 : Scan Min: {}'.format(scan_min))
            print('1 : Scan Max: {}'.format(scan_max))
            print('2 : Scan Resolution: {}'.format(scan_resolution))
            print('3 : Acquisition Time: {}'.format(acq_time))
            print('-'*50)
            # build_scan = np.arange(scan_min, self.scan_max, self.scan_resolution)
            # print('Estimated time for scan: {} minutes'.format(round((len(build_scan)*(self.acq_time+0.2))/60), 2))
            response = input('\nScan to commence (y/n). Enter integer values to change paramter:')

            if response == 'y':
                break
            elif response == 'n':
                return
            else:
                try:
                    response = int(response)
                    if response == 0:
                        scan_min = float(input('Enter new scan min:'))
                    elif response == 1:
                        scan_max = float(input('Enter new scan max:'))
                    elif response == 2:
                        scan_resolution = float(input('Enter new scan resolution:'))
                    elif response == 3:
                        acq_time = float(input('Enter new acquisition time:'))
                except ValueError:
                    print('Invalid input. Please enter an integer value')
                    continue
            
        print("Beginning scan...")
        print("Moving to initial grating position: {}".format(grating_wavelength))

        build_scan = np.arange(scan_min, scan_max, scan_resolution)
        self.process_coms('{} {}'.format(motor, scan_min))

        for idx, steps in enumerate(build_scan):

            if idx != 0:
                self.process_coms('{} {}'.format(motor, scan_resolution))
            time.sleep(0.1)
            response = self.process_coms('acq {}'.format(acq_time))
            time.sleep(0.1)
            data = self.extract_data(response)
            intensity = float(data[0])
            # print('{}:{}'.format(scan_pos, intensity))
            add_data_point([steps, intensity])
            # breakpoint()
            scan_results = np.vstack((scan_results, [steps, data[0], data[1]]))

        self.results = np.array(scan_results).astype(float)
        print(self.results)
        print('Returning to initial grating position: {}'.format(grating_wavelength))
        self.process_coms('{} {}'.format(motor, -(scan_max-scan_resolution)))
        filename = os.path.join(self.dataDir, '{}_motor_scan_results_{}.txt'.format(motor, len([file for file in os.listdir(self.dataDir) if 'scan_results' in file])))
        np.savetxt(filename, self.results)



    def run_scan_spectrum(self, plot=True):
        '''Function for scanning a spectrum with the ADP and plotting the results in real-time. Legacy code, needs updating'''
        # Create figure for plotting
        fig, ax = plt.subplots()
        xs = []  # List to store x-axis values (time steps)
        ys = []  # List to store y-axis values (data points)

        # Initialize plot
        line, = ax.plot(xs, ys, 'r-')  # 'r-' means red line
        ax.set_xlim(0, 10)  # Set initial x-axis limits
        ax.set_ylim(0, 1)  # Set initial y-axis limits

        # Display the plot
        plt.ion()
        plt.show()

        def add_data_point(newData):
            # Append new data points to the lists
            xs.append(float(newData[0]))
            ys.append(float(newData[1]))
            
            # Update line data
            line.set_data(xs, ys)
            
            # Adjust x-axis and y-axis limits dynamically
            ax.set_xlim(min(xs), max(xs))
            ax.set_ylim(min(ys) - 0.1, max(ys) + 0.1)
            
            # Redraw the plot
            plt.draw()
            plt.pause(0.01)

        # TODO: Eventually replace code to skip process_coms and call send_to_UNO


        print("custom scan")
        scan_results = np.empty((0, 3)).astype(float)
        grating_pos = self.get_grating_motor_positions()
        grating_wavelength = self.calculate_grating_wavelength(grating_pos)[0]


        while True:
            print('-'*50)
            print('Perparing wavelength scan. Current Parameters:')
            print('0 : Scan Min: {}'.format(self.scan_min))
            print('1 : Scan Max: {}'.format(self.scan_max))
            print('2 : Scan Resolution: {}'.format(self.scan_resolution))
            print('3 : Acquisition Time: {}'.format(self.acq_time))
            print('-'*50)
            build_scan = np.arange(self.scan_min, self.scan_max, self.scan_resolution)
            print('Estimated time for scan: {} minutes'.format(round((len(build_scan)*(self.acq_time+0.2))/60), 2))
            response = input('\nScan to commence (y/n). Enter integer values to change paramter:')

            if response == 'y':
                break
            elif response == 'n':
                return
            else:
                try:
                    response = int(response)
                    if response == 0:
                        self.scan_min = float(input('Enter new scan min:'))
                    elif response == 1:
                        self.scan_max = float(input('Enter new scan max:'))
                    elif response == 2:
                        self.scan_resolution = float(input('Enter new scan resolution:'))
                    elif response == 3:
                        self.acq_time = float(input('Enter new acquisition time:'))
                except ValueError:
                    print('Invalid input. Please enter an integer value')
                    continue
            
        print("Beginning scan...")
        print("Moving to initial grating position: {}".format(grating_wavelength))

        for idx, target in enumerate(build_scan):

            self.go_to_grating_wavelength(target)
            time.sleep(0.1)
            response = self.process_coms('acq {}'.format(self.acq_time))
            time.sleep(0.1)
            data = self.extract_data(response)
            intensity = float(data[0])
            # print('{}:{}'.format(scan_pos, intensity))
            add_data_point([target, intensity])
            # breakpoint()
            scan_results = np.vstack((scan_results, [target, data[0], data[1]]))

        self.results = np.array(scan_results).astype(float)
        print(self.results)
        print('Returning to initial grating position: {}'.format(grating_wavelength))
        self.go_to_grating_wavelength(grating_wavelength)
        filename = os.path.join(self.dataDir, 'spectrum_scan_results_{}.txt'.format(len([file for file in os.listdir(self.dataDir) if 'scan_results' in file])))
        np.savetxt(filename, self.results)


    def cli_commands(self):
        while True:
            coms = input('Enter command:\n')
            if coms == '':
                continue
            # com = [item.lower() for item in coms.split(' ')]
            try:
                coms = coms.strip(' ')
                response = self.process_coms(coms)
                if response is None:
                    continue
                if isinstance(response, int) or isinstance(response, float):
                    # already processed
                    continue
                
                data = self.extract_data(response)
                if len(data) > 0:
                    self.data.append(data)
            except Exception as e:
                # print('Error processing command', sys.exc_info()) 
                traceback.print_exc()
                print(e)
                continue


    

    


    
    # def send_command_to_apd(self, command):
    #     self.apd_serial.write('{}\r'.format(command).encode())
    #     time.sleep(0.01)
    #     # response = self.apd_serial.read(self.apd_serial.inWaiting())
    #     # print(response)
    #     # 

    # def set_acquisition_time(self, acq_time):
    #     self.send_command_to_apd('t{}\r'.format(acq_time))
    #     time.sleep(0.1)
    #     response = self.apd_serial.read(self.apd_serial.inWaiting())
    #     print(response)
    #     code = response.decode().strip('\r\n')
    #     if code.startswith('aa'):
    #         acq_time = float(code[2:])
    #         print('Master Receive - Acquisition time set to: {}'.format(acq_time))
    #     # 
    #     time.sleep(1)
    #     print(self.apd_serial.read(self.apd_serial.inWaiting()))




    # def serial_connect(self, serial_port, baud_rate=115200):
    #     try:
    #         # Establish a serial connection
    #         ser = serial.Serial(serial_port, baud_rate, timeout=1) 
    #         # print(ser)
    #         # ser.write('Test\r'.encode())
    #         time.sleep(self.pico_read_delay)
    #         response = ser.read(ser.inWaiting())
    #         print(response)
    #         return ser

        # except serial.SerialException as e:
        #     print(f"Error: {e}")

        # finally:
        #     if 'ser' in locals() and ser.is_open:
        #         ser.close()
        
    # def connect_to_marlin(self):
    #     ''' Current working pico-MARLIN-coms 19/01/24'''
    #     # Replace with your serial port and baud rate
    #     serial_port = 'COM4'  # or 'COM3' for Windows
    #     baud_rate = 115200  # Adjust as per your Pico's settings
    #     self.pico_read_delay = 0.1  # This is important! Some Picos need a delay before sending data

    #     comList = {

    #     }
    #     def get_mode():

    #         while True:
    #             currentMode = input('Enter the current mode: ramanmode or imagemode')
    #             if currentMode == 'ramanmode' or currentMode == 'imagemode':
    #                 return currentMode

    #     self.currentMode = get_mode()


    #     try:
    #         # Establish a serial connection
    #         ser = serial.Serial(serial_port, baud_rate, timeout=1) 
    #         # print(ser)
    #         ser.write('Test\r'.encode())
    #         time.sleep(self.pico_read_delay)
    #         response = ser.read(ser.inWaiting())
    #         print(response)
    #         return ser

    #     except serial.SerialException as e:
    #         print(f"Error: {e}")

    #     finally:
    #         if 'ser' in locals() and ser.is_open:
    #             ser.close()

    # def send_command_to_pico(self, command):

    #     if command[0] == 'flush':
    #         self.pico_marlin.flush()
    #         return
    #     if command[0] == self.currentMode:
    #         print('Error: alread in {} mode'.format(self.currentMode))
    #         return
    #     # command = command
    #     if command[0] in self.pico_dict.keys():
    #         if len(command) > 1:
    #             command = '{}{}'.format(self.pico_dict[command[0]], command[1]) # concatenate command if parameters are provided
    #         # command = self.pico_dict[command]
    #         else:
    #             command = self.pico_dict[command[0]]
    #     self.pico_marlin.write(f'{command}\r'.encode())
    #     self.pico_marlin.flush()

    #     # Read the response
    #     time.sleep(self.pico_read_delay)
    #     response = self.pico_marlin.read(self.pico_marlin.inWaiting())  # Read available bytes
    #     if response:
    #         print("Response from Pico:")
    #         print(response.decode().strip())
    #     else:
    #         print("No response received. Check the connection and settings.")



    def send_command_to_spectrometer(self, command, report=True):
                    # self.instrument.write(com)
                    # time.sleep(0.0001)
        # if len(command) > 1:
        #     command = '{}{}'.format(self.spectrometer_dict[command[0]], command[1]) # concatenate command if parameters are provided
        # else:
        #     command = self.spectrometer_dict[command[0]]
        # print(command)
        self.spectrometer.write(command)
        time.sleep(0.0001)
            # self.spectrometer.write(com)
        if command == 'A':
            count = 100
            while count > 0:
                print('Initialising: Sleeping for {} seconds'.format(count))
                time.sleep(1)
                count -= 1
        
        response = self.spectrometer.read()
        if report == True:
            print('RES:', response)
        return response

    def connect_to_spectrometer(self):
        # Open a connection to the instrument
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        self.spectrometer = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument

        self.spectrometer.write('WHERE AM I')
        time.sleep(0.0001)
        self.state = self.spectrometer.read()
        print(self.state)
        # 
        return self.spectrometer, self.state


    # def main(self):
    #     while True:
    #         try:
    #             # loop continuously here for com input
    #             # response = self.apd_serial.read(self.apd_serial.inWaiting())
    #             # response = self.uno_serial.read(self.uno_serial.inWaiting())
    #             # print(response)
    #             com = input('Enter command:\n')
    #             # if com == 'COM':
    #             #     while True:
    #             #         com = 'Enter string command:\n'
    #             #         # self.instrument.write(com)
    #             #         # time.sleep(0.0001)
    #             # else:
    #             # command = com.split(' ')
    #             self.send_command_to_UNO(com)
    #             self.read_command_from_uno()

    #             continue


    #             if com[0] in self.APD_comList:
    #                 self.send_command_to_apd(com)
    #                 time.sleep(0.1)
    #             elif com == 'read':
    #                 response = self.apd_serial.read(self.apd_serial.inWaiting())
    #                 print(response)
    #             else:
    #                 print('Command not recognized: {}'.format(com))
                
    #             continue


    #             # if command[0] == 'read':
    #             #     response = self.apd_serial.read(self.apd_serial.inWaiting())
    #             #     print('APD:', response)
    #             #     response = self.apd_serial.read(self.pico_marlin.inWaiting())
    #             #     print('pico_marlin:', response)

    #             # if command[0] == 't':
    #             #     self.set_acquisition_time(command[1])

    #                 # self.send_command_to_apd(struct.pack('<f', 0.12))
    #                 # self.send_command_to_apd(struct.pack('<f', 12))
    #                 # self.send_command_to_apd(struct.pack( .'<f', 45.6))

    #                 # self.send_command_to_apd(2.5)
    #                 # # time.sleep(0.001)
    #                 # self.send_command_to_apd('run')
    #                 # time.sleep(0.001)


    #             if command[0] in self.spectrometer_dict.keys():
    #                 self.send_command_to_spectrometer(command)
    #             elif command[0] in self.apd_dict.keys():
    #                 self.send_command_to_apd(self.apd_dict[command[0]])
    #             else:
    #                 self.send_command_to_pico(self.pico_dict[command[0]])
    #         except Exception as e:
    #             print(e) 

                    
def continuous():
    root = tk.Tk()
    gui = ArduinoInterface(root)

    root.mainloop()

def discon():
    microscope = Microscope()
    microscope.main()

def cli():
    microscope = Microscope(debug_skip=['laser', 'TRIAX'], unoCOM='COM10')
    # microscope.cli_commands()
    try:
        microscope.cli_commands()
    except Exception as e:
        # print("failed at line ", sys.exc_info())
        traceback.print_exc()
        print(e)

if __name__ == '__main__':
    # discon()
    # continuous()
    cli()


# class Spectrometer:

    def __init__(self):
        self.spectrometer, spectrometer_state = self.connect_to_spectrometer()

    def connect_to_spectrometer(self):
        # Open a connection to the instrument
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        spectrometer = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument
        # instrument = rm.open_resource('COM6')  # Replace with the actual VISA address of your instrument
        # s = serial.Serial(port='GPIB0::1::INSTR', timeout=5000)


    # def connect(instrument):
        spectrometer.write('O2000')
        time.sleep(0.0001)
        state = spectrometer.read()
        spectrometer.write('WHERE AM I')
        time.sleep(0.0001)
        state = spectrometer.read()
        print(state)
        # 
        return spectrometer, state





    def control_instrument(self, command):
        while True:
            try:
                # loop continuously here for com input
                com = input('Enter command - c to continue:\n')
                if com == 'c':
                    break
                spectrometer.write(com)
                if com == 'A':
                    count = 100
                    while count > 0:
                        print('Initialising: Sleeping for {} seconds'.format(count))
                        time.sleep(1)
                        count -= 1
                response = spectrometer.read()
                print('RES:', response)
            except Exception as e:
                print(e) 

        count = 0
        for x in range(10):
            spectrometer.write('F0,{}'.format(5000))
            response = spectrometer.read()
            print('moving to {}'.format(x*5000))
            # while response == 'b':
            # while True:
            #     # response = spectrometer.write('E')
            #     time.sleep(0.5)
            #     count+=1
            #     if count > 50:
            #         break
            time.sleep(0.5)
            # count += 1
                # print('waiting')
                
                # response = spectrometer.read()
                # if count > 50:
                #     print('timed out')
                #     break

            

            
            

        while True:
            try:
                com = input('Enter command:\n')
                spectrometer.write(com)
                response = spectrometer.read()
                print('RES:', response)
            except Exception as e:
                print(e) 
                

        # 
        # Read the response from the spectrometer

        try:
            response = spectrometer.read()
            print("Response:", response)
        except pyvisa .VisaIOError as e:
            if e.error_code == pyvisa.constants.VI_ERROR_TMO:
                print("Timeout expired. spectrometer did not respond.")
            else:
                print("An error occurred:", e)


        # Close the spectrometer connection
        spectrometer.close()


        #k0,0,100 = move slit 100 steps relative
        #j0,0<CR> = read slit pos
        #i0,0,0<CR> = set slit position (0)


# Note: pico-mk3-coms_V1.0.py is the working version. This wrapper is having issues with the com port.
# notes re: this version: marlin controller will only work if movement commands are sent. Anything else will break the read/write loop. need to move away from this marlin controller ASAP, or write a more robust coms wrapper.


