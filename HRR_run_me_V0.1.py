import gpib_ctypes
import pyvisa
import time
import serial
import struct

'''# looking for some kind of response like "b" or "o". Use command "O2000" to enter into command mode.
Initial grating is Blaze 500, 1200 g/mm
centre for 532 nm is roughly 241543
centre for sulfur at ~800 nm is 376886
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


    

class ArduinoInterface:
    def __init__(self, master):

        self.plot = DynamicPlotApp(master)

        self.microscope = Microscope()
        
        self.master = master
        master.title("Arduino Command Interface")


        # Setup the serial connection
        self.uno_serial = serial.Serial('COM8', 9600)  # Replace 'COM_PORT' with your actual COM port

        # Text box for command input
        self.command_entry = tk.Entry(master, width=50)
        self.command_entry.bind("<Return>", self.process_input)
        self.command_entry.pack()

        # box for scan min
        self.scan_min_entry = tk.Entry(master, width=10)
        self.scan_min_entry.insert(0, '-1000')
        self.scan_min_entry.bind("<Return>", self.update_scan_params)
        self.scan_min_entry.place(x=5, y=20)    
        # label for scan min
        self.scan_min_label = tk.Label(master, text="Scan Min")
        self.scan_min_label.place(x=70, y=20)    
        
        # box for scan max
        self.scan_max_entry = tk.Entry(master, width=10)
        self.scan_max_entry.insert(0, '1000')
        self.scan_max_entry.bind("<Return>", self.update_scan_params)
        self.scan_max_entry.place(x=5, y=40)
        # label for scan max
        self.scan_max_label = tk.Label(master, text="Scan Max")
        self.scan_max_label.place(x=70, y=40)


        # box for scan resolution
        self.scan_resolution_entry = tk.Entry(master, width=10)
        self.scan_resolution_entry.insert(0, '100')
        self.scan_resolution_entry.bind("<Return>", self.update_scan_params)
        self.scan_resolution_entry.place(x=5, y=60)
        # label for scan resolution
        self.scan_resolution_label = tk.Label(master, text="Scan Resolution")
        self.scan_resolution_label.place(x=70, y=60)

        # Button for sending commands
        self.send_button = tk.Button(master, text="Send Command", command=self.send_command)
        self.send_button.pack()

        # button for running the scan
        self.send_button = tk.Button(master, text="Run Scan", command=self.run_scan)
        self.send_button.pack()

        # Scrolled Text Area for displaying outputs
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=10)
        self.text_area.pack(pady=10)

        # Separate thread to continuously read from serial port
        self.read_thread = threading.Thread(target=self.read_from_uno)
        self.read_thread.daemon = True
        self.read_thread.start()

        self.get_grating_position()

    def update_labels(self):
        self.scan_resolution_label = tk.Label(self.master, text="Scan Resolution {}".format(self.scan_resolution))

    def update_scan_params(self, event=None):
        try:
            self.microscope.scan_min = float(self.scan_min_entry.get())
        except:
            pass
        try:
            self.microscope.scan_max = float(self.scan_max_entry.get())
        except:
            pass
        try:
            self.microscope.scan_resolution = float(self.scan_resolution_entry.get())
        except:
            pass
        # self.update_labels()

    def process_input(self, event=None):  # Event is passed by bind
        command = self.command_entry.get()
        split_command = command.split(' ')
        self.command_entry.delete(0, tk.END)  # Clear entry after sending
        if split_command[0] in self.microscope.spectrometer_dict.keys():
            response = self.microscope.send_command_to_spectrometer(split_command)
            self.update_text_area(response)
        else:
            self.send_command_to_UNO(command=command)
        
        # self.read_from_uno()


    def send_command_to_UNO(self, command=None, event=None):  # Event is passed by bind
        if not command:
            command = self.command_entry.get()
        self.uno_serial.write('{}\n'.format(command).encode())
        self.command_entry.delete(0, tk.END)  # Clear entry after sending

    def read_from_uno(self):
        while True:
            if self.uno_serial.in_waiting > 0:
                response = self.uno_serial.readline().decode().strip()
                # if response == '':  # Skip empty lines
                    # continue
                self.update_text_area(response)

    def update_text_area(self, message):
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.see(tk.END)  # Scroll to the bottom

    def send_command(self):
        self.send_command_to_UNO()

    def get_grating_position(self):
        response = self.microscope.send_command_to_spectrometer(['read_grating'])
        response = response.strip()

        grating_pos = int(response[1:])
        self.microscope.grating_pos = grating_pos
        self.update_text_area(response)



    def run_scan(self):
        pass
        self.acq_time = 1
        scan_results = np.empty((0, 2)).astype(float)
        self.get_grating_position()
        self.microscope.send_command_to_spectrometer(['grating', self.microscope.scan_min])
        for idx in np.arange(self.microscope.scan_min, self.microscope.scan_max, self.microscope.scan_resolution):
            self.microscope.send_command_to_spectrometer(['grating', self.microscope.scan_resolution])
            time.sleep(0.5)
            self.send_command_to_UNO('acq')
            time.sleep(self.acq_time)
            response = self.read_from_uno()
            intensity = float(response[response.index('#')+1:])
            # scan_results.append([step, response])
            scan_results = np.vstack((scan_results, [self.microscope.grating_pos, intensity]))
            self.plot.update_plot([self.microscope.grating_pos, intensity])
            self.update_text_area('Grating Position: {} - Intensity: {}'.format(self.microscope.grating_pos, intensity))
        self.results = np.array(scan_results).astype(float)
        print(self.results)
        pass

class Microscope:

    def __init__(self):

        self.scan_min = -1000
        self.scan_max = 1000
        self.scan_resolution = 100

        self.acq_time = 1
        self.centre_wavelength = 376886
        
        
        # commands for controlling TRIAX spectrometer
        self.spectrometer_dict = {
            'init': 'A',
            'comsmode': '02000',
            'read_grating': 'H0',
            'grating': 'F0,',
            'read_enter': 'j0,0',
            'read_exit': 'j0,3',
            'move_enter': 'k0,0,',
            'move_exit': 'k0,3,',
            'poll motors after move command sent': 'E',
            'ccd_mode': 'f0',
            'apd_mode': 'e0'
            #'entrance mirror to front enterance': 'c0',
            #'entrance mirror to side enterance': 'd0'
        }

        # commands for sample/stage motion and imaging beamsplitter
        self.stage_dict = {
            'X': 'X',
            'Y': 'Y',
            'Z': 'Z',
            'imagemode': 'G0 E-500',
            'ramanmode': 'G0 E500'
        }

        # commands for controlling laser properties
        self.laser_dict = {
            'lambda': 'lambda',
        }


        # commands for controlling APD
        self.apd_dict = {
            'run': 'run',
            'acq': 'acq',
            'time': 'time'
        }

        self.APD_comList = ['r', 'a', 't']

        self.spectrometer, self.state = self.connect_to_spectrometer()
        # self.pico_marlin = self.connect_to_marlin()
        self.apd_serial = self.connect_to_APD()
        self.uno_serial = self.connect_to_UNO()

    # def pack_floats(self, floats):
    #     return b','.join(struct.pack('<f', f) for f in floats)

    # def connect_to_APD(self):
    #     APD_serial = serial.Serial('COM7', 9600, timeout=1)
    #     return APD_serial
    
    def connect_to_UNO(self):
        UNO_serial = serial.Serial('COM8', 9600, timeout=1)
        return UNO_serial
    
    def send_command_to_UNO(self, command):
        self.uno_serial.write('{}\n'.format(command).encode())
        time.sleep(0.1)
        # response = self.uno_serial.read(self.uno_serial.inWaiting())
        # print(response)
        # breakpoint()

    def read_command_from_uno(self):
        response = ''
        while self.uno_serial.in_waiting > 0: #FIX: Change the logic to do this in the main loop
            response += self.uno_serial.readline().decode()
        # response = self.uno_serial.read(self.uno_serial.inWaiting()).decode().strip('\r\n')
        print(response)

    
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



    def send_command_to_spectrometer(self, command, report=False):
                    # self.instrument.write(com)
                    # time.sleep(0.0001)
        if len(command) > 1:
            command = '{}{}'.format(self.spectrometer_dict[command[0]], command[1]) # concatenate command if parameters are provided
        else:
            command = self.spectrometer_dict[command[0]]

        self.spectrometer.write(command)
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
        spectrometer = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument

        spectrometer.write('WHERE AM I')
        time.sleep(0.0001)
        state = spectrometer.read()
        print(state)
        # breakpoint()
        return spectrometer, state


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

if __name__ == '__main__':
    # discon()
    continuous()


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
                

        breakpoint()
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


