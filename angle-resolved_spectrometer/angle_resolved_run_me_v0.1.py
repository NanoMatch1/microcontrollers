import os
import serial
import struct
import time
import numpy as np
# // initial cal: X motor 0 angle: -10720 steps from limit switch
# // initial cal: X 10 deg, 9770 steps from vertical
# // initial cal: X 170 deg, -9680 steps from vertical

# // Initial cal: Y motor 0 angle: -10252 steps from limit switch
# // initial cal: Y 170 deg, 9680 steps from vertical
# // initial cal: Y 10 deg, -9680 steps from vertical
# (9680*2)/160

# class SpoofConnection:
#     '''This class is a stand-in for the serial connection to the Arduino'''
#     def __init__(self):
#         pass

#     def receive_command(self):
#         '''Receive a command from the Arduino'''
#         return input("Enter command: ")

class AngleResolvedSpectrometer:

    def __init__(self, serial_port='COM7', working_dir=None):
        self.uno_serial = serial.Serial(serial_port, 9600)
        time.sleep(2)

        if working_dir is None:
            working_dir = os.path.dirname(os.path.abspath(__file__))
        self.working_dir = working_dir

        # Calibration data (based on your provided calibration info)
        self.steps_per_degree = {
            'X': (9680*2)/160,  # Steps per degree for X axis
            'Y': (9680*2)/160,  # Steps per degree for Y axis
        }

        # Store current positions in steps (start at home position, 0 degrees)
        self.current_position = {'X': 0, 'Y': 0}  # Steps
        self.current_angle = {'X': 0, 'Y': 0}  # Degrees

        self.x_home = -10720
        self.y_home = -10252

        self.hard_limits = {
            'X': 10720,
            'Y': 10252,
        }

        self.measure_mode = 'specular'
        
        self.commandDict = {
            'wait': self.wait_for_motors,
            'home': self.home_motors,
            'a': self.go_to_angle,
            'wai': self.get_current_position,
            'basic': self.basic_scan,
        }

    def process_coms(self, command):
        cmd = command.split(' ')
        breakpoint()
        if len(cmd) > 1:
            command = cmd[0]
            args = cmd[1:]
            if command in self.commandDict:
                return self.commandDict[command](*args)
            else:
                return 'Invalid command'

        else:
            if command in self.commandDict:
                return self.commandDict[command]()
            else:
                return 'Invalid command'

    def home_motors(self):
        # Home both motors to 0 degrees
        # self.send_and_receive('mox{}'.format(self.x_home))
        # self.send_and_receive('moy{}'.format(self.y_home))

        self.send_command_to_UNO('home')

        self.send_command_to_UNO('mox{}'.format(self.x_home))
        self.send_command_to_UNO('moy{}'.format(self.y_home))

        self.current_position = {'X': 0, 'Y': 0}
        self.current_angle = {'X': 0, 'Y': 0}
        print("Motors homed to 0 degrees.")

    def angle_to_steps(self, axis, angle):
        """Convert angle to steps for the given axis."""
        steps = int(angle * self.steps_per_degree[axis])
        return steps

    def steps_to_angle(self, axis, steps):
        """Convert steps to angle for the given axis."""
        angle = steps / self.steps_per_degree[axis]
        return angle

    def go_to_angle(self, angle):
        """Move both motors to the given angle (specular reflectance mode)."""
        angle = float(angle)
        
        # Convert angle to steps for both motors
        x_target = self.angle_to_steps('X', angle)
        y_target = self.angle_to_steps('Y', angle)

        # Calculate relative movement from current position
        x_move_steps = x_target - self.current_position['X']
        y_move_steps = y_target - self.current_position['Y']

        # Send commands to motors
        print("sending command")
        self.send_command_to_UNO('mox{}'.format(x_move_steps))
        self.send_command_to_UNO('moy{}'.format(y_move_steps))

        # Wait for motors to finish moving
        # self.wait_for_motors()

        # Update current positions and angles
        self.current_position['X'] = x_target
        self.current_position['Y'] = y_target
        self.current_angle['X'] = angle
        self.current_angle['Y'] = angle

        print(f"Motors moved to {angle} degrees (specular).")

    def wait_for_motors(self, delay=0.2):
        """Wait until the motors are done moving."""
        while True:
            self.send_command_to_UNO('isrun')
            time.sleep(delay)
            response = self.read_from_serial_until()
            if response and response[0] == 'S0':
                break
            time.sleep(delay)

    def send_command_to_UNO(self, command):
        """Send a command to the Arduino."""
        self.uno_serial.write('{}\n'.format(command).encode())
        time.sleep(0.1)

    def read_command_from_uno(self):
        """Read response from Arduino."""
        response = ''
        while self.uno_serial.in_waiting > 0:
            response += self.uno_serial.readline().decode()
            # print(response)
        return response.strip()

    def read_from_serial_until(self, end_flag='#CF', report=False):
        """Read from serial until end flag is encountered."""
        responses = []
        while True:
            response = self.read_command_from_uno()
            if response == '':
                time.sleep(0.01)
                continue
            if report:
                print(response)
            # breakpoint()
            if end_flag in response:
                response = response[:-len('\r\n'+end_flag)]
                responses.append(response)
                return responses
            
            responses.append(response)


    def send_and_receive(self, command):
        '''Blocking. waits until axes are done'''
        """Send a command to Arduino and get the response."""
        self.send_command_to_UNO(command)
        return self.read_from_serial_until()

    def get_current_position(self):
        """Retrieve current position of motors."""
        self.send_command_to_UNO('pos')
        time.sleep(0.1)
        response = self.read_from_serial_until()
        pos = response[0][2:-2].split(',')
        current_steps = (int(pos[0]), int(pos[1]))
        self.current_position = {'X': int(pos[0]), 'Y': int(pos[1])}
        self.current_angle = {'X': self.steps_to_angle('X', self.current_position['X']),
                              'Y': self.steps_to_angle('Y', self.current_position['Y'])}
        
        print(f'X: {self.current_angle["X"]}, Y: {self.current_angle["Y"]}')
        
    def run_scan(self, start_angle, end_angle, resolution):
        series_name = input("Enter series name: ")
        self.scan_log = []
        """Run a scan from start to end angle with given step size."""
        if abs(self.angle_to_steps('X', start_angle)) > self.hard_limits['X']:
            print("Start angle exceeds hard limit for X motor.")
            return
        if abs(self.angle_to_steps('Y', start_angle)) > self.hard_limits['Y']:
            print("Start angle exceeds hard limit for Y motor.")
            return
        
        angles = np.arange(start_angle, end_angle + resolution, resolution)
        print("Scan to commence at angles: ", angles)
        input("Press Enter to start the scan...")
        os.makedirs(os.path.join(self.working_dir, series_name), exist_ok=True)

        for angle in angles:
            self.go_to_angle(angle)
            self.scan_log.append([self.current_angle['X'], self.current_angle['Y']])
            input("Collect data at this angle and press Enter to continue...")
            # Do something with the spectrometer here
            # For example, take a measurement at the current angle
            # and store the data for further

    def rename_files(self, series_name, angles):
        """Rename files in the current directory with a given prefix and suffix."""
        # This is just a placeholder function for demonstration
        # takes the files that have been generated by the spectrometer and renames then with the correct angles
        pass

    def basic_scan(self, start_angle, end_angle, resolution):
        """Run a basic scan from start to end angle with given step size."""
        start_angle = float(start_angle)
        end_angle = float(end_angle)
        resolution = float(resolution)
        angles = np.arange(start_angle, end_angle + resolution, resolution)
        print("Scan to commence at angles: ", angles)
        input("Press Enter to start the scan...")

        for angle in angles:
            self.go_to_angle(angle)
            input("Collect data at this angle and press Enter to continue...")
            # Do something with the spectrometer here
            # For example, take a measurement at the current angle
            # and store the data for further

    def main_loop(self):
        """Main loop to receive commands."""
        while True:
            cmd = input("Enter command: ").strip().lower()

            if cmd.startswith('a'):
                angle = cmd.split(' ')[1]
                self.go_to_angle(angle)

            elif cmd == 'pos':
                self.get_current_position()
                print(f"Current positions: X: {self.current_angle['X']} degrees, Y: {self.current_angle['Y']} degrees")
            elif cmd == 'home':
                self.home_motors()
            elif cmd == 'exit':
                break
            elif cmd in self.commandDict:
                self.process_coms(cmd)
            elif cmd.startswith('z'):
                angle = cmd.split(' ')[1]
                self.send_command_to_UNO('moz{}'.format(angle))
            else:
                self.process_coms(cmd)
                print("Invalid command")

# Instantiate the spectrometer
ars = AngleResolvedSpectrometer()

ars.main_loop()

# range is 15 deg (0/1) - 75 (1-13)
# z ~600 steps/90 deg


# TODO: change the final homing step to return to 15 degrees
# balance armature masses to reduce the load on the motors
# decrease motor current