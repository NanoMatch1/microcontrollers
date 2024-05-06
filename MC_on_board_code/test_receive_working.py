import machine
import time
import struct
import select
import sys

from machine import UART
os.dupterm(uart)
uart = UART(0, baudrate=115200)  # Assuming you're using UART0
uart.init(115200, bits=8, parity=None, stop=1)  # Modify these parameters as needed
#uart = machine.UART(0, 115200)
# os.dupterm(uart)

def receive_floats(uart):
#     received_data = uart.readline()
    if received_data:
        floats = struct.unpack('<' + 'f' * (len(received_data) // 4), received_data)
        return floats
    return None

# UART setup (adjust pins and baudrate as needed)
# uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

# f = open("{}.txt".format('im_a_file'), "a")
# f.write("Now the file has more content!")
# f.close()

def wait_for_command(echo = False ):
    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.readline()
#             print(ch)SS
#             print(ch.decode())
#             value, = struct.unpack('<f', ch[1:])
            command = ch.strip()
            if command[0] == 'a':
#                 print('yep')
#                 print('aa{}'.format(command[1:]))
                try:
                    acq_time = float(command[1:])
                except TypeError:
                    print("Error - {} not recognised as a time. Please enter a float or int.".format(command[1:]))
                
                print('aa{}'.format(acq_time))
#             print('COM:{}\n'.format(command))
#             command = ch.split('\')
#             command = command[0]
#             command = command[:-4]
#             command = command.strip('\r\n')
#             print(command)

#             print(value)
            
#             for x in ch:
#                 print(x)
#             ch = ch.strip()
#             if echo:
#                 print(ch)
#             command = ch.split(' ')
#             command = ch
#             print('APD Pico received {}\end'.format(command))
#             print('APD com:')
#             print(command)
            return command
        else:
            time.sleep(0.01)
            continue

# Main loop
while True:
#     received_floats = receive_floats(uart)
    try:
        received = wait_for_command()
        
        if received:
#             floats = struct.unpack('<' + 'f' * (len(received_floats) // 4), received_floats)

            
#             print("Received floats:", received_floats)
            output = 'string_out'
            f = open("{}.txt".format(output), "a")
#             f.write('|'.join([str(x) for x in received_floats]))
#             f.write('#')
            f.write(received)
            f.close()
#             print(received)
        time.sleep(0.1)
    except Exception as e:
        print(e)