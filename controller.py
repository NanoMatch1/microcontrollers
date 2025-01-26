import serial
import time

from instruments import simulate

class ArduinoUNO:

    def __init__(self, unoCOM='COM10', baud=9600, report=True):
        self.unoCOM = unoCOM
        self.baud = baud
        self.report = report

        # if the firmware commands change, update this dictionary
        self.message_map = {
            'get_grating_positions': 'Apos',
        }

        self.response_map = {
            # 'get_grating_positions': self._process_grating_positions,
        }

    def connect(self, unoCOM, baud):
        self.serial = self._connect_to_UNO(unoCOM, baud)

    def send_command(self, command):
        self._send_command_to_UNO(self.message_map[command])
        return self._read_from_serial_until()

    def get_grating_motor_positions(self):
        response = self.send_command(self.message_map['get_grating_positions'])
        
        positions = response[0].split(':')[1]
        positions = positions.strip('<P>P')
        positions = positions.split(',')
        grating_steps = [float(x[1:]) for x in positions]
        
        return grating_steps
    
    def get_laser_motor_positions(self):
        response = self.send_command(self.message_map['get_laser_positions'])
        
        positions = response[0].split(':')[1]
        positions = positions.strip('<P>P')
        positions = positions.split(',')
        laser_steps = [float(x[1:]) for x in positions]
        
        return laser_steps

    def _connect_to_UNO(self, unoCOM, baud):
        UNO_serial = serial.Serial(unoCOM, baud, timeout=1)
        while UNO_serial.in_waiting == 0:
            time.sleep(0.1)
        while UNO_serial.in_waiting > 0:
            response = UNO_serial.readline().decode().strip()
            print(response)
        return UNO_serial
    
    def _send_command_to_UNO(self, command):
        self.serial.write('{}\n'.format(command).encode())
        time.sleep(0.1)

    def _read_command_from_uno(self):
        response = ''
        while self.serial.in_waiting > 0:
            response += self.serial.readline().decode()
        return response

    def _read_from_serial_until(self, end_flag='#CF'):
        end_responses = []

        while True:
            response = self.read_command_from_uno()
            
            if response == '':
                time.sleep(0.01)
                continue

            if self.report is True:
                print(response)
            split_responses = response.split('\r\n')
            for item in split_responses:
                if item == end_flag:
                    return end_responses
                if item != '':
                    end_responses.append(item)

            time.sleep(0.01)





    
