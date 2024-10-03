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

class AngleResolvedSpectrometer:

    def __init__(self, serial_port='COM7'):
        self.uno_serial = serial.Serial(serial_port, 9600)
        time.sleep(2)

        self.current_position = [0, 0, 0]

        self.calibration = (9680*2)/160 # steps per degree
        self.x_home = -10720
        self.y_home = -10252

        self.measure_mode = 'specular'
        
        self.commandDict = {
            # 'pos': 'pos',
            # 'setpos': 'setpos',
            'wait': self.wait_for_motors,
            'home': self.home_motors,
            'a': self.go_to_angle,
        }


    def process_coms(self, command):
        cmd = command.split(' ')
        if len(cmd) > 1:
            command = cmd[0]
            args = cmd[1:]
        if command in self.commandDict:
            return self.commandDict[command](*args)
        else:
            return 'Invalid command'
        
    def initialise(self):
        pass

    def home_motors(self):
        self.send_command_to_UNO('homex')
        time.sleep(0.1)
        response = self.read_from_serial_until()
        # print(response)
        breakpoint()
        homing_positions = response[0].split(',')

        self.send_and_receive('mox{}'.format(self.x_home))
        self.send_and_receive('moy{}'.format(self.y_home))

        print("Finished homing")

        
    # @property
    # def current_position(self):
    #     # return self.
    #     pass

    def wait_for_motors(self, delay=0.1):
        count = 0
        running_A = True
        while running_A is True:

            if running_A is True:
                # response = self.process_coms('Aisrun')
                self.send_command_to_UNO('isrun')
                # res = response[0].split(':')[0]
                # res1 = self.extract_coms_message(response)
                time.sleep(delay)
                response = self.read_from_serial_until()
                res1 = response[0]
                # 
                # breakpoint()

                if res1 == 'S0':
                    running_A = False
                # elif res1 == 'R1':
                else:
                    # print("A running")
                    time.sleep(delay)
                    continue

            if count > 0:
                print("Loop broke")
                
            count += 1

        return 'S0'
    
    def go_to_angle(self, angle):
        self.send_and_receive('mox{}'.format(angle))
        self.send_and_receive('moy{}'.format(angle))

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
    
    
    def read_command_from_uno(self):
        # print('reading command from uno')
        response = ''
        while self.uno_serial.in_waiting > 0: #FIX: Change the logic to do this in the main loop
            # print(response)
            response += self.uno_serial.readline().decode()
        # response = self.uno_serial.read(self.uno_serial.inWaiting()).decode().strip('\r\n')
        # print('Finihsed reading command from uno: {}'.format(response))
        return response
    
    def get_current_position(self):
        self.send_command_to_UNO('pos')
        time.sleep(0.1)
        response = self.read_from_serial_until()
        print(response)
        response = response[0][2:-2]
        pos = response.split(',')
        self.current_position = [int(pos[0]), int(pos[1]), int(pos[2])]

    def send_and_receive(self, command):
        self.send_command_to_UNO(command)
        time.sleep(0.1)
        response = self.read_from_serial_until()
        print(response)


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
    
    def run_series(self, start_angle, stop_angle, resolution):
        angles = np.arange(start_angle, stop_angle, resolution)
        for angle in angles:
            self.go_to_angle(angle)
            self.wait_for_motors()
            # self.get_current_position()
            input("angle: {}. Acquire, then press enter to continue".format(angle))
            # print(self.current_position)
            time.sleep(0.1) 

    def main_loop(self):
        while True:
            cmd = input("Enter command (move/query/stop/exit): ").strip().lower()

            if cmd.startswith('x') or cmd.startswith('y') or cmd.startswith('z'):
                self.send_command_to_UNO('mo{}'.format(cmd))
                time.sleep(0.1)
                response = self.read_from_serial_until()
                print(response)
            elif cmd == 'pos':
                self.get_current_position()

            else:
                self.process_coms(cmd)


ars = AngleResolvedSpectrometer()
# Command loop
try:
    ars.main_loop()
except Exception as e:
    print(e)


