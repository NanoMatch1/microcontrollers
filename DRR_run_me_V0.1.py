import gpib_ctypes
import pyvisa
import time
import serial
import struct
import threading
import matplotlib.animation as animation
import json

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

class Microscope:

    calibration_backup = {"wl_triax_steps": [0.10804683994803718, 331.8588098129754, 43950.89354704326], "triax_steps_wl": [-8.032233265071597e-10, 0.002589893546654974, -65.392713732836], "laser": [-0.42078367938194094, 13.182099307902691], "grating": [1.0370034283344927, 10.925199912128772], "wavelength_laser": [-0.013186836473750425, -41.70675588176, 41979.647251902534], "wavelength_grating": [9.14706131106529, -7363.889052419929], "steps_laser": [-5.094413299766325e-08, -0.01590813394008432, 802.7653861488677], "steps_grating": [0.10924618909058334, 805.0765596939007]}

    def __init__(self, debug_skip=[], unoCOM='COM8'):

        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.scriptDir, 'data')
        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)

        if os.path.exists(os.path.join(self.scriptDir, 'calibrations.json')):
            with open(os.path.join(self.scriptDir, 'calibrations.json'), 'r') as f:
                self.calibrations = json.load(f)
                print('Calibrations loaded from file')
        
        else:
            self.calibrations = self.calibration_backup
            print('Calibration file not found, using backup')

        self.cal_laser1_to_laser2 = np.poly1d(self.calibrations['laser'])
        self.cal_grating1_to_grating2 = np.poly1d(self.calibrations['grating'])
        self.cal_wavelength_to_laser_steps = np.poly1d(self.calibrations['wavelength_laser'])
        self.cal_wavelength_to_grating_steps = np.poly1d(self.calibrations['wavelength_grating'])
        self.cal_laser_steps_to_wavelength = np.poly1d(self.calibrations['steps_laser'])
        self.cal_grating_steps_to_wavelength = np.poly1d(self.calibrations['steps_grating'])
        self.cal_wavelength_to_triax_steps = np.poly1d(self.calibrations['wl_triax_steps'])
        self.cal_triax_steps_to_wavelength = np.poly1d(self.calibrations['triax_steps_wl'])

        self.scan_min = -1000
        self.scan_max = 1000
        self.scan_resolution = 50

        self.acq_time = 1
        self.centre_wavelength = 376886

        self.data = []

        self.microscope_functions = {
            'scan': self.run_scan_custom,
            'get_grating_position': self.get_grating_position,
            'scan_min': self.set_scan_min,
            'scan_max': self.set_scan_max,
            'scan_res': self.set_scan_resolution,
            'acq_time': self.set_acquisition_time,
            'sl': self.go_to_laser_wavelength,
            'sd': self.go_to_grating_wavelength,
            'shift': self.go_to_grating_wavelength,
            'wai': self.get_all_current_positions,
            'reference': self.reference_calibration,
            # 'setpos': self.set_absolute_positions
        }
        
        

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

            'getposa': 'Apos',
            'gpa' : 'Apos',
            'getposb': 'Bpos',
            'gpb' : 'Bpos',

        }

        # additive position: Y -12984, subtractive = 0

        self.acquisition_dict = {
            'acq': 'acq', 
            'run': 'run',

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
            self.uno_serial = self.connect_to_UNO(unoCOM)
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

    def get_all_current_positions(self):
        self.current_wavelength = self.calculate_laser_position()
        self.current_grating_wavelength = self.calculate_grating_position()

        print('Current laser wavelength: {}'.format(self.current_wavelength))
        print('Current grating wavelength: {}'.format(self.current_grating_wavelength))
        
    def get_laser_motor_positions(self):
        print('entered get laser')
        try:
            response = self.process_coms('gpa')
            print('got response')
            positions = response[1].split(':')[1]
            positions = positions.strip('<P>P')
            positions = positions.split(',')
            laser_pos = [float(x[1:]) for x in positions]
        except Exception as e:
            print('Error getting laser position')
            print(e)
            return
        
        print('Current laser pos: {}'.format(laser_pos))
        return laser_pos
    
    def get_grating_motor_positions(self):
        try:
            response = self.process_coms('gpb')
            positions = response[1].split(':')[1]
            positions = positions.strip('<P>P')
            positions = positions.split(',')
            laser_pos = [float(x[1:]) for x in positions]
        except Exception as e:
            print('Error getting grating position')
            print(e)
            return
        
        print('Current grating pos: {}'.format(laser_pos))
        return laser_pos
    
    def calculate_laser_position(self, current_pos=None):
        current_laser_pos = self.get_laser_motor_positions()
        l1_pos = current_laser_pos[0]
        # l2_pos = current_laser_pos[1]

        l1_wavelength = self.cal_laser_steps_to_wavelength(l1_pos)
        # print('Current laser wavelength: {}'.format(l1_wavelength))
        return l1_wavelength


    def calculate_grating_position(self):
        current_grating_pos = self.get_grating_motor_positions()
        g1_pos = current_grating_pos[0]
        g2_pos = current_grating_pos[1]
        g1_wavelength = self.cal_grating_steps_to_wavelength(g1_pos)

        return g1_wavelength

    def go_to_laser_wavelength(self, wavelength):
        '''Currently operating as movements in relative mode. Add feature in the future to move in absolute mode.
        Uses the calibrations to move the laser motors into position for a specified wavelength.'''
        # breakpoint()
        # if self.current_mode == 'additive':
        #     target_pos = self.cal_wavelength_to_laser_steps(wavelength)
        # elif self.current_mode == 'subtractive':
        #     target_pos = self.cal_wavelength_to_grating_steps(wavelength)
        try:
            wavelength = float(wavelength)
        except ValueError:
            print('Invalid value for wavelength - use a number')
            return

        current_pos = self.get_laser_motor_positions()
        if current_pos is None:
            return 

        l1_target = round(self.cal_wavelength_to_laser_steps(wavelength))
        # print("l1 target: {}".format(l1_target))

        l2_target = round(self.cal_laser1_to_laser2(l1_target))
        # print("l2 target: {}".format(l2_target))
        print('Current laser position: {}'.format(current_pos))
        print('Target laser position: {}'.format([l1_target, l2_target]))
        move_l1 = l1_target - current_pos[0]
        move_l2 = l2_target - current_pos[1]
        print("moving l1 by {}".format(move_l1))

        # self.move_to(target_pos)
        if move_l1 != 0:
            response = self.process_coms('l1 {}'.format(move_l1))
        if move_l2 != 0:
            response = self.process_coms('l2 {}'.format(move_l2))

        print('Laser excitation at {}'.format(wavelength))


    
    def go_to_grating_wavelength(self, wavelength):
        '''Currently operating as movements in relative mode. Add feature in the future to move in absolute mode.'''
        try:
            wavelength = float(wavelength)
        except ValueError:
            print('Invalid value for wavelength - use a number')
            return

        current_pos = self.get_grating_motor_positions()
        if current_pos is None:
            return 

        g1_target = self.cal_wavelength_to_grating_steps(wavelength)
        # print("l1 target: {}".format(g1_target))

        g2_target = self.cal_grating1_to_grating2(g1_target)
        # print("l2 target: {}".format(g2_target))
        move_g1 = round(g1_target - current_pos[0])
        move_g2 = round(g2_target - current_pos[1])

        # self.move_to(target_pos)
        if move_g1 != 0:
            response = self.process_coms('g1 {}'.format(move_g1))
        if move_g2 != 0:
            response = self.process_coms('g2 {}'.format(move_g2))

        print('Grating detection at {}'.format(wavelength))

    def reference_calibration(self, steps):
        '''Used to reference the current motor position to the laser wavelength, as defined by the current calibration. Measure a spectrum on the TRIAX and enter the stepper motor position and pixel count of the peak wavelength here. In the future, this will be automated with a peak detection algorithm.'''
        # Instructions: Ensure that the entire system is well aligned, and that the stepper motors are in the correct positions relative to one another for passing the laser wavelength to the spectrograph.
        # Centre the laser peak in pixel 50 of the CCD. Enter the stepper motor position here.
        true_wavelength = self.cal_triax_steps_to_wavelength(float(steps))
        print('True wavelength: {}. Moving motors to true wavelength'.format(true_wavelength))
        
        # Set 
        l1_target = round(self.cal_wavelength_to_laser_steps(true_wavelength))
        l2_target = round(self.cal_laser1_to_laser2(l1_target))
        g1_target = round(self.cal_wavelength_to_grating_steps(true_wavelength))
        g2_target = round(self.cal_grating1_to_grating2(g1_target))

        self.set_absolute_positions_A(f'{l1_target},{l2_target},0,0')
        self.set_absolute_positions_B(f'{g1_target},{g2_target},0,0')

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
            # breakpoint()
            response = self.read_from_serial_until()
            # print(response)
            # breakpoint()
            gpa = response[1].split('<P')[1]
            gpa = gpa.split('P>')[0]
            gpa = gpa.split(',')

            command = 'o{}o'.format(self.tuning_motor_dict['gpb'])
            # print('UI>UNO:{}'.format(command))
            self.send_command_to_UNO(command)
            time.sleep(0.1)
            # breakpoint()
            response = self.read_from_serial_until()
            # print(response)
            gpb = response[1].split('<P')[1]
            gpb = gpb.split('P>')[0]
            gpb = gpb.split(',')

            
            with open(os.path.join(self.scriptDir, 'eept.txt'), 'a') as f:
                f.write('{}:{}:{}\n'.format(gpa, gpb, extra))
            print(f'exporting {gpa}:{gpb}:{extra}')
            return (f'exporting {gpa}:{gpb}')
            

        if com[0] in self.general_dict.keys():
            self.general_dict[com[0]]()
            response = 'Connected to {}'.format(com[0])

        elif com[0] in self.acquisition_dict.keys():
            if len(com) > 1:
                command = 'm{} {}m'.format(self.acquisition_dict[com[0]], com[1])
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
            # breakpoint()
            response = self.read_from_serial_until()
            # print(response)
            return response
            # breakpoint()
        
        elif com[0] in self.laser_dict.keys():

            command = self.laser_dict[com[0]]
            self.send_command_to_laser(command)
            time.sleep(0.01)
            # response = self.laser_serial.read(self.laser_serial.inWaiting())
            response = self.read_from_laser()
            print(response)
            return response
            # breakpoint()

        elif com[0] in self.microscope_functions.keys():
            if len(com) > 1:
                response = self.microscope_functions[com[0]](com[1])
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
        # breakpoint()

    def connect_to_UNO(self, unoCOM='COM8'):
        UNO_serial = serial.Serial(unoCOM, 9600, timeout=1)
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
        new_data = []
        for item in response:
            if item.startswith("COUNTS:"):
                try:
                    value = item[item.index(':')+2:item.index('/')]
                    timestamp = item[item.index('/')+1:]
                    new_data = [float(value), float(timestamp)]
                except Exception as e:
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

    def run_scan_custom(self, plot=True):
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
        response_list = self.process_coms('getpos')

        stepper_pos = {}
        for item in response_list:
            if '<P' in item:
                positions = item.split('P')[1]
                positions = positions.split(',')
                for pos in positions:
                    stepper_pos[pos[0]] = int(pos[1:]) # position in steps -> refer to calibration dataset for conversion
        print("Established current motor positions:", stepper_pos)
        self.grating_pos = stepper_pos['Y']
        scan_pos = self.grating_pos
        scan_dims = np.arange(self.grating_pos + self.scan_min, self.grating_pos + self.scan_max, self.scan_resolution)
        print(scan_dims)
        input('\nScan to commence:')
        self.process_coms('A {}'.format(self.scan_min))
        scan_pos += self.scan_min
        print("Beginning scan...")
        time.sleep(0.5)
        for idx, val in enumerate(scan_dims):
            if idx != 0:
                self.process_coms('A {}'.format(self.scan_resolution))
                scan_pos += self.scan_resolution
            time.sleep(0.1)
            response = self.process_coms('acq {}'.format(self.acq_time))
            time.sleep(0.1)
            data = self.extract_data(response)
            intensity = float(data[0])
            print('{}:{}'.format(scan_pos, intensity))
            add_data_point([scan_pos, intensity])
            scan_results = np.vstack((scan_results, [scan_pos, data[0], data[1]]))

        self.results = np.array(scan_results).astype(float)
        print(self.results)
        self.process_coms('A {}'.format(self.grating_pos-scan_pos))
        filename = os.path.join(self.dataDir, 'scan_results_{}.txt'.format(len([file for file in os.listdir(self.dataDir) if 'scan_results' in file])))
        np.savetxt(filename, self.results)

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
    #     # breakpoint()
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
            coms = coms.strip(' ')
            response = self.process_coms(coms)
            if response is None:
                continue
            data = self.extract_data(response)
            if len(data) > 0:
                self.data.append(data)


    

    


    
    # def send_command_to_apd(self, command):
    #     self.apd_serial.write('{}\r'.format(command).encode())
    #     time.sleep(0.01)
    #     # response = self.apd_serial.read(self.apd_serial.inWaiting())
    #     # print(response)
    #     # breakpoint()

    # def set_acquisition_time(self, acq_time):
    #     self.send_command_to_apd('t{}\r'.format(acq_time))
    #     time.sleep(0.1)
    #     response = self.apd_serial.read(self.apd_serial.inWaiting())
    #     print(response)
    #     code = response.decode().strip('\r\n')
    #     if code.startswith('aa'):
    #         acq_time = float(code[2:])
    #         print('Master Receive - Acquisition time set to: {}'.format(acq_time))
    #     # breakpoint()
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
        # breakpoint()
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
    try:
        microscope.cli_commands()
    except Exception as e:
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
        # breakpoint()
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
                

        # breakpoint()
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


