import gpib_ctypes
import pyvisa
import time
import serial
import struct
import threading
import matplotlib.animation as animation
import json
import sys
import traceback
from types import SimpleNamespace
from dataclasses import dataclass


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

import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import serial
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os

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


    

# class ArduinoInterface:
#     def __init__(self, master):

#         self.plot = DynamicPlotApp(master)
#         self.microscope = Microscope()
        
#         self.master = master
#         master.title("Arduino Command Interface")


#         # Setup the serial connection
#         self.uno_serial = serial.Serial('COM8', 9600)  # Replace 'COM_PORT' with your actual COM port

#         # Text box for command input
#         self.command_entry = tk.Entry(master, width=50)
#         self.command_entry.bind("<Return>", self.process_input)
#         self.command_entry.pack()

#         # box for scan min
#         self.scan_min_entry = tk.Entry(master, width=10)
#         self.scan_min_entry.insert(0, '-1000')
#         self.scan_min_entry.bind("<Return>", self.update_scan_params)
#         self.scan_min_entry.place(x=5, y=20)    
#         # label for scan min
#         self.scan_min_label = tk.Label(master, text="Scan Min")
#         self.scan_min_label.place(x=70, y=20)    
        
#         # box for scan max
#         self.scan_max_entry = tk.Entry(master, width=10)
#         self.scan_max_entry.insert(0, '1000')
#         self.scan_max_entry.bind("<Return>", self.update_scan_params)
#         self.scan_max_entry.place(x=5, y=40)
#         # label for scan max
#         self.scan_max_label = tk.Label(master, text="Scan Max")
#         self.scan_max_label.place(x=70, y=40)


#         # box for scan resolution
#         self.scan_resolution_entry = tk.Entry(master, width=10)
#         self.scan_resolution_entry.insert(0, '100')
#         self.scan_resolution_entry.bind("<Return>", self.update_scan_params)
#         self.scan_resolution_entry.place(x=5, y=60)
#         # label for scan resolution
#         self.scan_resolution_label = tk.Label(master, text="Scan Resolution")
#         self.scan_resolution_label.place(x=70, y=60)

#         # Button for sending commands
#         self.send_button = tk.Button(master, text="Send Command", command=self.send_command)
#         self.send_button.pack()

#         # button for running the scan
#         self.send_button = tk.Button(master, text="Run Scan", command=self.run_scan)
#         self.send_button.pack()

#         # Scrolled Text Area for displaying outputs
#         self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=10)
#         self.text_area.pack(pady=10)

#         # Separate thread to continuously read from serial port
#         self.read_thread = threading.Thread(target=self.read_from_uno)
#         self.read_thread.daemon = True
#         self.read_thread.start()

#         self.get_grating_position()

#     def update_labels(self):
#         self.scan_resolution_label = tk.Label(self.master, text="Scan Resolution {}".format(self.scan_resolution))

#     def update_scan_params(self, event=None):
#         try:
#             self.microscope.scan_min = float(self.scan_min_entry.get())
#         except:
#             pass
#         try:
#             self.microscope.scan_max = float(self.scan_max_entry.get())
#         except:
#             pass
#         try:
#             self.microscope.scan_resolution = float(self.scan_resolution_entry.get())
#         except:
#             pass
#         # self.update_labels()

#     def process_input(self, event=None):  # Event is passed by bind
#         command = self.command_entry.get()
#         split_command = command.split(' ')
#         self.command_entry.delete(0, tk.END)  # Clear entry after sending
#         if split_command[0] in self.microscope.spectrometer_dict.keys():
#             response = self.microscope.send_command_to_spectrometer(split_command)
#             self.update_text_area(response)
#         else:
#             self.send_command_to_UNO(command=command)
        
#         # self.read_from_uno()


#     def send_command_to_UNO(self, command=None, event=None):  # Event is passed by bind
#         if not command:
#             command = self.command_entry.get()
#         self.uno_serial.write('{}\n'.format(command).encode())
#         self.command_entry.delete(0, tk.END)  # Clear entry after sending

#     def read_from_uno(self):
#         while True:
#             if self.uno_serial.in_waiting > 0:
#                 response = self.uno_serial.readline().decode().strip()
#                 # if response == '':  # Skip empty lines
#                     # continue
#                 self.update_text_area(response)

#     def update_text_area(self, message):
#         self.text_area.insert(tk.END, message + '\n')
#         self.text_area.see(tk.END)  # Scroll to the bottom

#     def send_command(self):
#         self.send_command_to_UNO()

#     def get_grating_position(self):
#         response = self.microscope.send_command_to_spectrometer(['read_grating'])
#         response = response.strip()

#         grating_pos = int(response[1:])
#         self.microscope.grating_pos = grating_pos
#         self.update_text_area(response)



#     # def run_scan(self):
#         pass
#         self.acq_time = 1
#         scan_results = np.empty((0, 2)).astype(float)
#         self.get_grating_position()
#         self.microscope.send_command_to_spectrometer(['grating', self.microscope.scan_min])
#         for idx in np.arange(self.microscope.scan_min, self.microscope.scan_max, self.microscope.scan_resolution):
#             self.microscope.send_command_to_spectrometer(['grating', self.microscope.scan_resolution])
#             time.sleep(0.5)
#             self.send_command_to_UNO('acq')
#             time.sleep(self.acq_time)
#             response = self.read_from_uno()
#             intensity = float(response[response.index('#')+1:])
#             # scan_results.append([step, response])
#             scan_results = np.vstack((scan_results, [self.microscope.grating_pos, intensity]))
#             self.plot.update_plot([self.microscope.grating_pos, intensity])
#             self.update_text_area('Grating Position: {} - Intensity: {}'.format(self.microscope.grating_pos, intensity))
#         self.results = np.array(scan_results).astype(float)
#         print(self.results)
#         pass

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

    def __init__(self, debug_skip=[], unoCOM='COM8'):

        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.scriptDir, 'data')
        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)

        self.generate_calibrations(report=True)

        self.scan_min = 800
        self.scan_max = 835
        self.scan_resolution = 0.5

        # self.grating_calib = calibrations['']

        self.grating_steps = None
        self.laser_steps = None

        self.current_wavelength = None
        self.current_shift = 0
        self.monochromator_mode = 'subtractive'
        self.pinhole = None
        # self.to_addivite = -12990 -13108+39 

        self.acq_time = 1
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
            'gshut': self.move_grating_shutter,
            'readldr': self.read_ldr0,
            'debug': self.print_debug,
            'calibrate': self.run_calibration

            # 'changemode': self.change_monochromator_mode,
            # 'setpos': self.set_absolute_positions
            # additive reference at 220: [83, -13108...]

        }
        
        # -12858 (0 optically)
        # -12973 (220 optically and 220 mechanically)


        # commands for controlling TRIAX spectrometer
        self.spectrometer_dict = {
            'init': 'A',
            'comsmode': '02000',
            'read_grating': 'H0',
            'rg': 'H0',
            'grating': 'F0,',
            'g': 'F0,',
            'read_enter': 'j0,0',
            'ren': 'j0,0',
            'read_exit': 'j0,3',
            'rex': 'j0,3',
            'move_enter': 'k0,0,',
            'men': 'k0,0,',
            'move_exit': 'k0,3,',
            'mex': 'k0,3,',
            'poll motors after move command sent': 'E',
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
            'acq': 'acq', 
            'run': 'run',
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
            'laser': self.connect_to_laser
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


    def run_calibration(self, wavelength_range: tuple, resolution: float):
        calibrationDict = {}

        if isinstance(wavelength_range, str):
            vals = wavelength_range.split(',')
            wavelength_range = (float(vals[0]), float(vals[1]))

        resolution = float(resolution)

        breakpoint()
        
        wavelengths = np.arange(*wavelength_range, resolution)
        print("Running calibration for wavelengths: ", wavelengths)
        cond = input("Continue? (y/n): ")
        if cond.lower() == 'n':
            return
        
        for wl in wavelengths:
            
            self.go_to_laser_wavelength(wl)
            self.go_to_grating_wavelength(wl)
            
            breakpoint()
    
    def run_ldr_scan(self, step_number):
        pass

    def print_debug(self):
        print('Entering print debug')
        breakpoint()

    def read_ldr0(self):
        response = self.process_coms('rldr00')
        print("LDR0:", int(response[0][1:]))
        # breakpoint()
        # print(response)

    def move_grating_shutter(self, state):
        if state == 'open' or state == 'o':
            self.process_coms('gsh off')
        elif state == 'close' or state == 'c':
            self.process_coms('gsh on')

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

    def generate_calibrations(self, report=False):
        if os.path.exists(os.path.join(self.scriptDir, 'calibrations.json')):
            with open(os.path.join(self.scriptDir, 'calibrations.json'), 'r') as f:
                calibrations = json.load(f)
                print('Calibrations loaded from file')
        
        else:
            calibrations = Microscope.calibration_backup
            print('Calibration file not found, using backup')
        
        self.all_calibrations = calibrations
        self.calibrations = SimpleNamespace()
        
        for name, calib in calibrations.items():
            if report:
                print(name, calib, "poly" if len(calib) == 3 else "poly_sin")
            if len(calib) == 7:
                self.calibrations.__setattr__(name, PolySinModulation(*calib))
            else:
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
        report = {
            'monochromator mode': self.monochromator_mode,
            'laser l1, l2 lambda': self.current_laser_wavelength,
            'g1 lambda': self.current_grating_wavelength,
            'laser motor positions': self.get_laser_motor_positions(),
            'grating motor positions': self.get_grating_motor_positions(),
            'laser wavenumber': self.current_laser_wavenumber,
            'grating wavenumber': self.current_raman_wavenumber,
            'Raman wavelength': self.current_raman_wavelength,
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


    @property
    def current_grating_wavelength(self):
        return self.calculate_grating_position()

    @property
    def current_laser_wavelength(self):
        return self.calculate_laser_position()
    
    @property
    def current_laser_wavenumber(self):
        '''Takes the current raman shift and calculates the corresponding wavelength (i.e. for the detector calibration).'''
        return 10_000_000/self.current_laser_wavelength[0]
         
    @property
    def current_raman_wavelength(self):
        '''Calculates the current wavelength that corresponds to the current Raman shift at this excitation wavelength.'''
        return 10_000_000/self.current_raman_wavenumber

    
    @property
    def current_raman_wavenumber(self):
        '''Takes the current laser wavenumber and calculates the absolute wavenumber for the current raman shift.'''
        return self.current_laser_wavenumber - self.current_shift
    
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
        current_laser_wavelength, l2_wavelength = self.calculate_laser_position(current_laser_pos)
        current_grating_pos = self.get_grating_motor_positions()
        current_grating_wavenumber = self.current_raman_wavenumber
        # What the current wavelength should be at the detector
        current_detector_wavelength = self.wavenumber_to_wavelength(current_grating_wavenumber)
        print(current_detector_wavelength)
# Write function to store Raman shift on microcontrollers and get it back.


# Current laser pos: [175.0, -58.0, 0.0, 0.0]
# entered turning dict
# UI>UNO:oBposo
# UNO>B:pos
# <PX125,Y87,Z0,A0P>
# UI<UNO<B:<PX125,Y87,Z0,A0P>
# Current grating pos: [125.0, 87.0, 0.0, 0.0]
# Current laser wavelength: 799.9799025452799
# Current grating wavelength: 818.7323333302236
# Enter command:

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
        new_laser_wavelength, l2_wavelength = self.calculate_laser_position(new_laser_pos)
        new_grating_pos = self.get_grating_motor_positions()
        new_grating_wavelength = self.calculate_grating_position(new_grating_pos)[0]
        
        if new_grating_pos[0] == g1_target and new_grating_pos[1] == g2_target and new_laser_pos[0] == l1_target and new_laser_pos[1] == l2_target:
            print('Calibration shift successful')
            print('New Positions:\n Laser: {}\n Grating: {}'.format(new_laser_wavelength, new_grating_wavelength))
        else:
            print('Calibration shift failed')
            print('New Positions:\n Laser: {}\n Grating: {}'.format(new_laser_wavelength, new_grating_wavelength))


#     Current laser pos: [1.0, 13.0, 0.0, 0.0]
# entered turning dict
# UI>UNO:oBposo
# UNO>B:pos
# <PX9,Y47,Z0,A0P>
# UI<UNO<B:<PX9,Y47,Z0,A0P>
# Current grating pos: [9.0, 47.0, 0.0, 0.0]
# Current laser wavelength: 802.7494779639835
# Current grating wavelength: 806.0597753957159
# Enter command:



    def extract_coms_message(self, message):
        return message[1].split(':')[1].strip(' ')

    def wait_for_motors(self, delay=0.5):
        count = 0
        running_A = True
        running_B = True
        while running_A is True and running_B is True:

            if running_A is True:
                response = self.process_coms('Aisrun')
                # res = response[0].split(':')[0]
                res1 = self.extract_coms_message(response)
                # 
                if res1 == 'S0':
                    running_A = False
                # elif res1 == 'R1':
                else:
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
                    continue
                
            if count > 0:
                print("Loop broke")
                
            count += 1

            # print()


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
            if positions[0] == targets[0] and positions[1] == targets[1]:
                break
            time.sleep(0.2)

        print('Motors at target positions')
    
        # 

    def get_all_current_positions(self):
        l1_wavelength, l2_wavelength = self.calculate_laser_position()

        b_positions = self.calculate_grating_position()
        g1_wavelength = b_positions[0]
        g2_wavelength = b_positions[1]
        pin_pos = b_positions[2]
        g2_pos = self.get_grating_motor_positions()
        l1_pos = self.get_laser_motor_positions()

        
        print('Current laser pos: {}'.format(l1_pos))
        print('Current grating pos: {}'.format(g2_pos))
        self.current_wavelength = l1_wavelength

        print('Current l1 wavelength: {}'.format(l1_wavelength))
        print('Current l2 wavelength: {}'.format(l2_wavelength))
        print('Current g1 wavelength: {}'.format(g1_wavelength))
        print('Current g2 wavelength: {}'.format(g2_wavelength))
        print('Current pinhole position: {}'.format(pin_pos))

        # TODO: Change to @property
        # self.current_grating_wavelength = self.calculate_grating_position()

        # print('Current laser wavelength: {}'.format(self.current_wavelength))
        # print('Current grating wavelength: {}'.format(self.current_grating_wavelength))

        return 
        
    def get_laser_motor_positions(self):
        print('entered get laser')
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
    
    def calculate_laser_position(self, current_pos=None):
        if current_pos is None:
            current_laser_pos = self.get_laser_motor_positions()
        else:
            current_laser_pos = current_pos

        l1_pos = current_laser_pos[0]
        l2_pos = current_laser_pos[1]

        l1_wavelength = self.calibrations.l1_to_wl(l1_pos)
        l2_wavelength = self.calibrations.l2_to_wl(l2_pos)
        
        # print('Current laser wavelength: {}'.format(l1_wavelength))
        return l1_wavelength, l2_wavelength
    
# monochromator mode: additive
# laser lambda: 747.9912874168725
# g1 lambda: 760.3230930312565
# laser motor positions: [3406.0, -1425.0, 0.0, 0.0]
# grating motor positions: [-413.0, -12667.0, 0.0, 0.0]
# laser wavenumber: 13369.139678797854
# grating wavenumber: 13151.139678797854
# Raman wavelength: 760.3903725638248
# Raman shift: 218.0
# --------------------
# Enter command:


    def calculate_grating_position(self, current_pos=None):
        if current_pos is None:
            current_grating_pos = self.get_grating_motor_positions()
        else:
            current_grating_pos = current_pos

        g1_pos = current_grating_pos[0]
        g2_pos = current_grating_pos[1]
        pin_pos = current_grating_pos[2]

        # if self.monochromator_mode == 'additive':
        #     g2_pos = g2_pos - self.to_addivite

        g1_wavelength = self.calibrations.g1_to_wl(g1_pos)
        g2_wavelength = self.calibrations.g2_to_wl(g2_pos)

        return (g1_wavelength, g2_wavelength, pin_pos)

    def go_to_wavenumber(self, wavenumber):
        try:
            wavenumber = float(wavenumber)
        except ValueError:
            print('Invalid value for wavenumber - use a number')
            return
        if self.current_wavelength is None:
            self.get_all_current_positions()
        
        # ;
        # laser_wavenumber = 10_000_000/self.current_wavelength
        laser_wavenumber = self.current_laser_wavenumber
        # 
        wave = laser_wavenumber - wavenumber
        new_wavelength = 10_000_000/wave
        self.go_to_grating_wavelength(new_wavelength)
        self.current_shift = wavenumber
        print('Moving to wavenumber: {} for {} nm excitation'.format(wavenumber, self.current_wavelength))

    def go_to_laser_wavelength(self, wavelength):
        '''Currently operating as movements in relative mode. Add feature in the future to move in absolute mode.
        Uses the calibrations to move the laser motors into position for a specified wavelength.'''
        # 
        self.close_pinhole_shutter() # every time the laser moves the shutter should close. A final check for light on the LDR should be added before opening the shutter to minimise chances of laser damage on detector #TODO: Add this check

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

        self.wait_for_motors_manual([l1_target, l2_target, 0, 0], 'A')

        if backlash:
            response = self.process_coms('l1 -20')
            response = self.process_coms('l2 -20')
            time.sleep(0.1)
            response = self.process_coms('l1 20')
            response = self.process_coms('l2 20')

        print('Laser excitation at {}'.format(wavelength))
        self.open_pinhole_shutter() # add check that light levels are safe #TODO: Add this check

    def close_pinhole(self):
        response = self.process_coms('pin 0')
        print('Pinhole fully closed')

    def open_pinhole(self):
        response = self.process_coms('pin 160')
        print('Pinhole fully opened')

    def close_pinhole_shutter(self):
        response = self.process_coms('gshut on')
        print('Pinhole g shutter closed')

    def open_pinhole_shutter(self):
        response = self.process_coms('gshut off')
        print('Pinhole g shutter opened')

    def pinhole_shutter(self, state):
        if state == 'open':
            self.open_pinhole_shutter()
        elif state == 'closed':
            self.close_pinhole_shutter()

    def go_to_grating_wavelength(self, wavelength):
        '''Currently operating as movements in relative mode. Add feature in the future to move in absolute mode.'''

        self.close_pinhole_shutter() # every time the laser moves the shutter should close. A final check for light on the LDR should be added before opening the shutter to minimise chances of laser damage on detector #TODO: Add this check

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

        self.wait_for_motors_manual([g1_target, g2_target, 0, 0], 'B')
        # time.sleep(5)
        if backlash:
            response = self.process_coms('g1 -20')
            response = self.process_coms('g2 -20')
            time.sleep(0.1)
            response = self.process_coms('g1 20')
            response = self.process_coms('g2 20')

        print('Grating detection at {}'.format(wavelength))
        self.open_pinhole_shutter() # add check that light levels are safe #TODO: Add this check


            



    def reference_calibration(self, steps):
        '''Used to reference the current motor position to the laser wavelength, as defined by the current calibration. Measure a spectrum on the TRIAX and enter the stepper motor position and pixel count of the peak wavelength here. In the future, this will be automated with a peak detection algorithm.'''
        # Instructions: Ensure that the entire system is well aligned, and that the stepper motors are in the correct positions relative to one another for passing the laser wavelength to the spectrograph.
        # Centre the laser peak in pixel 50 of the CCD. Enter the stepper motor position here.
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

            laser_wavelength, l2_wavelength = self.calculate_laser_position()
            grating_wavelength = self.current_raman_wavelength

            
            with open(os.path.join(self.scriptDir, 'aapt.txt'), 'a') as f:
                f.write('{}:{}:{}:{}\n'.format(laser_wavelength, gpa, gpb, grating_wavelength))
            print(f'exporting {laser_wavelength}:{gpa}:{gpb}:{grating_wavelength}')
            return (f'exporting {laser_wavelength}:{gpa}:{gpb}:{grating_wavelength}')
            
            # sulfur REF: 210 sd (220 peak)
            # init got response

            # (785, 500), (800, 500)
            # 750 at 4543
            
# Current laser pos: [192.0, -65.0, 0.0, 0.0]
# entered turning dict
# UI>UNO:oBposo
# UNO>B:pos
# <PX-49,Y-13108,Z0,A0P>
# UI<UNO<B:<PX-49,Y-13108,Z0,A0P>
# Current grating pos: [-49.0, -13108.0, 0.0, 0.0]
# Current laser wavelength: 799.7091464278527
# Current grating wavelength: 799.7234964284621

# aligned manually to 0 shift:
# Current laser pos: [192.0, -65.0, 0.0, 0.0]
# entered turning dict
# UI>UNO:oBposo
# UNO>B:pos
# <PX-49,Y-12865,Z0,A0P>
# UI<UNO<B:<PX-49,Y-12865,Z0,A0P>
# Current grating pos: [-49.0, -12865.0, 0.0, 0.0]
# Current laser wavelength: 799.7091464278527
# Current grating wavelength: 799.7234964284621


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
            print('entered turning dict')
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

        # elif com[0] in self.apd_dict.keys():
        #     if len(com) > 1:
        #         command = '{} {}'.format(self.apd_dict[com[0]], com[1])
        #     else:
        #         command = self.apd_dict[com[0]]
        #     self.send_command_to_UNO(command)
        #     time.sleep(0.1)
        #     # response = self.read_command_from_uno()
        #     response = self.read_from_serial_until()

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

    # def extract_data_old(self, response):
    #     new_data = []
    #     for item in response:
    #         if item.startswith("#DAT"):
    #             try:
    #                 new_data.append(float(item[4:]))
    #             except Exception as e:
    #                 print('Error processing data')
    #                 print(e)
    #     return new_data
    
    def extract_data(self, response):
        if type(response) == float: # TODO: change this to detect data type better
            return
        new_data = []
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
        self.grating_pos = grating_pos
        print('Grating Pos: {}'.format(response))
        return grating_pos



    # def run_scan_custom(self, plot=True):


    #     # Create figure for plotting
    #     fig, ax = plt.subplots()
    #     xs = [0]  # List to store x-axis values (time steps)
    #     ys = [0]  # List to store y-axis values (data points)

    #     # Initialize plot
    #     line, = ax.plot(xs, ys, 'r-')  # 'r-' means red line

    #     def init():
    #         ax.set_xlim(0, 10)  # Set initial x-axis limits
    #         ax.set_ylim(0, 1)  # Set initial y-axis limits
    #         return line,

    #     def update_plot(frame):
    #         # Update line data
    #         line.set_data(xs, ys)
            
    #         # Adjust x-axis and y-axis limits dynamically
    #         ax.set_xlim(min(xs), max(xs))
    #         ax.set_ylim(min(ys), max(ys))
            
    #         return line,

    #     # Create an animation
    #     ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=100)

    #     # Display the plot
    #     plt.ion()
    #     plt.show()

    #     def add_data_point(newData):
    #         # Append new data points to the lists
    #         xs.append(newData[0])
    #         ys.append(newData[1])
    #         plt.draw()

    #     def scan():
    #         # TODO: Eventually replace code to skip process_coms and call send_to_UNO
    #         self.scan_min = 0
    #         self.scan_max = 10
    #         self.scan_res = 1
    #         self.acq_time = 0.5

    #         print("custom scan")
    #         scan_results = np.empty((0, 3)).astype(float)
    #         response_list = self.process_coms('getpos')

    #         stepper_pos = {}
    #         for item in response_list:
    #             if '<P' in item:
    #                 positions = item.split('P')[1]
    #                 positions = positions.split(',')
    #                 for pos in positions:
    #                     stepper_pos[pos[0]] = int(pos[1:]) # position in steps -> refer to calibration dataset for conversion
    #         print("Established current motor positions:", stepper_pos)
    #         self.grating_pos = stepper_pos['Y']
    #         scan_pos = self.grating_pos
    #         scan_dims = np.arange(self.grating_pos + self.scan_min, self.grating_pos + self.scan_max, self.scan_res)
    #         print(scan_dims)
    #         input('\nScan to commence:')
    #         self.process_coms('A {}'.format(self.scan_min))
    #         scan_pos += self.scan_min
    #         print("Beginning scan...")
    #         time.sleep(0.5)
    #         for idx, val in enumerate(scan_dims):
    #             if idx != 0:
    #                 self.process_coms('A {}'.format(self.scan_res))
    #                 scan_pos += self.scan_res
    #             time.sleep(0.1)
    #             response = self.process_coms('acq {}'.format(self.acq_time))
    #             time.sleep(0.1)
    #             data = self.extract_data(response)
    #             intensity = float(data[0])
    #             print('{}:{}'.format(scan_pos, intensity))
    #             add_data_point([scan_pos, intensity])
    #             scan_results = np.vstack((scan_results, [scan_pos, data[0], data[1]]))

    #         self.results = np.array(scan_results).astype(float)
    #         print(self.results)
    #         self.process_coms('A {}'.format(self.grating_pos-scan_pos))
    #         filename = os.path.join(self.dataDir, 'scan_results_{}.txt'.format(len([file for file in os.listdir(self.dataDir) if 'scan_results' in file])))
    #         np.savetxt(filename, self.results)

    #     # Run the scan in a separate thread
    #     scan_thread = threading.Thread(target=scan)
    #     scan_thread.start()

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
        grating_wavelength = self.calculate_grating_position(grating_pos)[0]
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
        grating_wavelength = self.calculate_grating_position(grating_pos)[0]


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

        # calshift 0
#         Current laser pos: [193.0, -66.0, 0.0, 0.0]
# entered turning dict
# UI>UNO:oBposo
# UNO>B:pos
# <PX-49,Y-13070,Z0,A0P>
# UI<UNO<B:<PX-49,Y-13070,Z0,A0P>
# Current grating pos: [-49.0, -13070.0, 0.0, 0.0]
# Current laser wavelength: 799.6932186804214
# Current grating wavelength: 799.7234964284621


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


        # current values:
#         Current laser pos: [192.0, -65.0, 0.0, 0.0]
# entered turning dict
# UI>UNO:oBposo
# UNO>B:pos
# <PX82,Y-12973,Z0,A0P>
# UI<UNO<B:<PX82,Y-12973,Z0,A0P>
# Current grating pos: [82.0, -12973.0, 0.0, 0.0]
# Current laser wavelength: 799.7091464278527
# Current grating wavelength: 814.0347471993285

#Calshift

# Current laser pos: [193.0, -66.0, 0.0, 0.0]
# entered turning dict
# UI>UNO:oBposo
# UNO>B:pos
# <PX82,Y-13165,Z0,A0P>
# UI<UNO<B:<PX82,Y-13165,Z0,A0P>
# Current grating pos: [82.0, -13165.0, 0.0, 0.0]
# Calibration shift successful
# New Positions:
#  Laser: 799.6932186804214
#  Grating: 814.0347471993285
# Enter command:


    # def run_scan_TRIAX(self, plot=True):
    #     scan_results = np.empty((0, 2)).astype(float)
    #     self.grating_pos = self.get_grating_position()
    #     initial_pos = self.grating_pos
    #     current_pos = initial_pos
    #     scan_dims = np.arange(self.grating_pos + self.scan_min, self.grating_pos + self.scan_max, self.scan_resolution)
    #     print(scan_dims)
    #     input('\nScan to commence:')
    #     self.send_command_to_spectrometer('F0, {}'.format(self.scan_min))
    #     current_pos += self.scan_min
    #     print("Beginning scan...")
    #     time.sleep(0.5)
    #     for idx, val in enumerate(scan_dims):
    #         if idx != 0:
    #             self.send_command_to_spectrometer('F0, {}'.format(self.scan_resolution))
    #             current_pos += self.scan_resolution
    #         time.sleep(0.5)
    #         self.send_command_to_UNO('oDacq{}o'.format(self.acq_time))
    #         # time.sleep(self.acq_time)
    #         # response = self.read_from_uno()
    #         response = self.read_from_serial_until()
    #         data = self.extract_data(response)
    #         if len(data) > 1:
    #             print("data is bigger than expected - change code to accommodate array of data")
    #         intensity = float(data[0])
    #         # scan_results.append([step, response])
    #         # scan_pos = self.grating_pos+(idx*self.scan_resolution)
    #         print('{} : {}'.format(current_pos, intensity))
    #         scan_results = np.vstack((scan_results, [current_pos, intensity]))
    #         # self.plot.update_plot([self.microscope.grating_pos, intensity])
    #         # self.update_text_area('Grating Position: {} - Intensity: {}'.format(self.microscope.grating_pos, intensity))
    #     self.results = np.array(scan_results).astype(float)
    #     print(self.results)
    #     # return to start pos
    #     self.send_command_to_spectrometer('F0, {}'.format(initial_pos-current_pos))
    #     print('Initial pos: {}'.format(initial_pos))
    #     print('Current pos: {}'.format(current_pos))
    #     print('Difference: {}'.format(current_pos-initial_pos))
    #     # 
    #     filename = os.path.join(self.dataDir, 'scan_results_{}.txt'.format(len([file for file in os.listdir(self.dataDir) if 'scan_results' in file])))
    #     np.savetxt(filename, self.results)
    #     if plot:
    #         # self.plot_scan_results(self.results)
    #         plt.plot(self.results[:, 0], self.results[:, 1])
    #         plt.show()


#662(200):469


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


