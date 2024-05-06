import struct
import time
import serial


# flt = [1.3, 1.6, 2]

# st = ','.join([str(f) for f in flt])


# breakpoint()

# Define delimiter (example)
DELIMITER = b','
# Define command types (example)
COMMAND_TYPE_FLOAT = 0x01
COMMAND_TYPE_INT = 0x02

def send_floats(serial, floats):
    # Pack the floats into binary format
    data = DELIMITER.join(struct.pack('<f', f) for f in floats)
    # Send the binary data over serial
    serial.write(data)
    time.sleep(0.01)

# Example usage
# send_floats(apd_serial, [3.14, 2.718, 1.618])


class SerialCommandSender:
    def __init__(self, serial):
        self.serial = serial
    
    def send_float_command(self, value):
        # Pack the command and value into binary format
        data = struct.pack('<Bf', COMMAND_TYPE_FLOAT, value)

        print(data)
        breakpoint()
        # Send the binary data over serial
        self.serial.write(data)
        time.sleep(0.01)
    
    def send_int_command(self, value):
        # Pack the command and value into binary format
        data = struct.pack('<Bi', COMMAND_TYPE_INT, value)
        # Send the binary data over serial
        self.serial.write(data)
        time.sleep(0.01)

class SerialCommandReceiver:
    def __init__(self, serial):
        self.serial = serial
    
    def receive_command(self):
        # Read the header byte to determine the command type
        header_byte = self.serial.read(1)
        if header_byte:
            command_type = ord(header_byte)
            if command_type == COMMAND_TYPE_FLOAT:
                # Read the float value
                data = self.serial.read(4)
                if data:
                    value = struct.unpack('<f', data)[0]
                    return command_type, value
            elif command_type == COMMAND_TYPE_INT:
                # Read the integer value
                data = self.serial.read(4)
                if data:
                    value = struct.unpack('<i', data)[0]
                    return command_type, value
        return None
    
def serial_connect(serial_port, baud_rate=115200):

    # Establish a serial connection
    ser = serial.Serial(serial_port, baud_rate, timeout=1) 
    # print(ser)
    # ser.write('Test\r'.encode())
    # time.sleep(self.pico_read_delay)
    response = ser.read(ser.inWaiting())
    print(response)
    return ser

ser = serial_connect('COM5')

send_floats(ser, [3.14, 2.718, 1.618])

time.sleep(0.1)
response = ser.read(ser.inWaiting())
print('From Pico: ', response)

# # Example usage
# sender = SerialCommandSender(ser) 
# sender.send_float_command(3.14)

# receiver = SerialCommandReceiver(ser)
# command = receiver.receive_command()
# if command:
#     command_type, value = command
#     print("Received command type:", command_type)
#     print("Received value:", value)
