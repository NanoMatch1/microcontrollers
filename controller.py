import serial
import time

from instruments import simulate

class ArduinoUNO:

    def __init__(self, unoCOM='COM10', baud=9600, report=True):
        self.unoCOM = unoCOM
        self.baud = baud
        self.report = report

    def connect(self, unoCOM, baud):
        self.serial = self.connect_to_UNO(unoCOM, baud)

    def connect_to_UNO(self, unoCOM, baud):
        UNO_serial = serial.Serial(unoCOM, baud, timeout=1)
        while UNO_serial.in_waiting == 0:
            time.sleep(0.1)
        while UNO_serial.in_waiting > 0:
            response = UNO_serial.readline().decode().strip()
            print(response)
        return UNO_serial
    
    def _send_command(self, command):
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





    
