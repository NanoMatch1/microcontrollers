import serial
import time

def connect_to_pico(port, baud_rate=115200):
    try:
        ser = serial.Serial(port=port, baudrate=baud_rate, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=0, rtscts=0, dsrdtr=False)
        print('Connected on {}'.format(port))
        ser.flushInput()
        ser.flushOutput()
        return ser
    except Exception as e:
        print(f"Could not connect: {e}")
        return None

def send_command(ser, command):
    if ser is None:
        print("Serial object is None. Cannot send command.")
        return
    command = '{}\r\n'.format(command)
    ser.write(command.encode())
    # ser.write(b'\n')  # End of Line (EOL) character, can vary based on your MicroPython setup

def read_response(ser):
    if ser is None:
        print("Serial object is None. Cannot read response.")
        return
    
    ser.read()
    
    # if ser.in_waiting:
    #     return ser.read(ser.in_waiting).decode('utf-8')
    
    return None

def receive(ser) -> str:
    line = ser.read_until('\r'.encode('UTF8'))
    return line.decode('UTF8').strip()

if __name__ == "__main__":
    # Replace 'COMx' with the actual port your Pico is connected to
    ser = connect_to_pico("COM9")
    print(ser)
    # ser.flushInput()
    # ser.flushOutput()
    
    # breakpoint()

    if ser is not None:
        while True:
            command = input("Enter command: ")
            
            send_command(ser, command)
            val = ser.read()
            print(val)
            breakpoint()
            # print(ser.in_waiting)

            # breakpoint()
            time.sleep(0.1)  # May need to adjust based on your specific requirements

            # breakpoint()
            
            response = read_response(ser)
            print(f"Received: {response}")
            
            if command == "exit":
                break


# # import serial
# # import serial.tools.list_ports
# # import codecs
# # import time

# # '''Establishes a serial connection over COM port and sends and receives data'''

# # def find_com_ports():
# #     com_ports = []
# #     ports = list(serial.tools.list_ports.comports())
# #     for port in ports:
# #         com_ports.append(port.device)
# #     return com_ports

# # def try_connecting_to_ports(com_ports):
# #     for port in com_ports:
# #         try:
# #             ser = serial.Serial(port, 115200, timeout=1)
# #             print(f"Connected to {port}")
# #             return ser
# #         except serial.SerialException:
# #             print(f"Failed to connect to {port}")
# #             continue
# #     return None

# # def search_and_connect():
# #     com_ports = find_com_ports()
# #     if not com_ports:
# #         print("No COM ports found.")
# #         return
    
# #     print(f"Found COM ports: {com_ports}")
    
# #     ser = try_connecting_to_ports(com_ports)
# #     if ser is None:
# #         print("Couldn't connect to any COM port.")
# #     else:
# #         return ser



# # def main(COM=None, gcode=True):
# #     if COM is None:
# #         s = search_and_connect()
# #     else:
# #         s = serial.Serial(COM, 9600)# parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=1)
# #     s.flushInput()
# #     s.flushOutput()

# #     # s.write("a thing\r".encode())
# #     # mes = s.read_until().strip()
# #     # print(mes.decode())
# #     while True:
# #         com = get_input()
# #         if gcode:
# #             send_gcode(s, com)
# #         else:
# #             send_command(s, com)

# # def get_input():
# #     com = input('Enter Command: \n')
# #     return com

# # def send_command(ser, com):
# #     # ser.flushInput()
# #     ser.flushOutput()
# #     ser.write('{}\r'.format(com).encode())
# #     # mes = ser.read_until().strip()
# #     mes = ser.readline()
# #     print(mes.decode())

# # def send_gcode(ser, com, report=True):
# #     # ser.flushInput()
# #     # ser.flushOutput()

# #     ser.write((str(com)+'\n').encode())

# #     if report:
# #         start = time.time()
# #         while not ser.in_waiting:
# #             pass
        
# #         finish = time.time()
# #         difference = finish - start
# #         print(f"Waited {difference} seconds for response")
        
# #         # if ser.in_waiting:
# #         #     all_data = ser.read(ser.in_waiting).decode('utf-8')
# #         #     print(all_data)

# #         while ser.in_waiting:
# #             line = ser.readline().decode('utf-8').strip()
# #             print(line)
    
# #     else:
# #         ser.flushOutput()

# #     # grbl_out = ser.readline() # Wait for grbl response with carriage return
# #     # print(grbl_out)
# #     # # print(grbl_out.decode())
# #     # try:
# #     #     print(grbl_out.decode('utf-8'))
# #     # except UnicodeDecodeError:
# #     #     print("Could not decode using UTF-8. Raw output:", grbl_out)

# #     # print(' : ' + str(grbl_out.strip()))

        
# # if __name__ == '__main__':
# #     main()

# # #M106  - Fan on
# # #M107  - Fan off

# import serial
# class Talker:
#     TERMINATOR = '\r'.encode('UTF8')

#     def __init__(self, timeout=1):
#         self.serial = serial.Serial('COM9', 115200, timeout=timeout)

#     def send(self, text: str):
#         line = '%s\r\n' % text
#         self.serial.write(line.encode('utf-8'))
#         reply = self.receive()
#         reply = reply.replace('>>> ','') # lines after first will be prefixed by a propmt
#         if reply != text: # the line should be echoed, so the result should match
#             raise ValueError('expected %s got %s' % (text, reply))

#     def receive(self) -> str:
#         line = self.serial.read_until(self.TERMINATOR)
#         return line.decode('UTF8').strip()

#     def close(self):
#         self.serial.close()


# t = Talker()
# t.send('print("hello world")')
# t.send('led.value(0)')
# breakpoint()
# print('end')