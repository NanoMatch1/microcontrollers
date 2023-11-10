import serial
import serial.tools.list_ports
import codecs
import time

'''Establishes a serial connection over COM port and sends and receives data'''

def find_com_ports():
    com_ports = []
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        com_ports.append(port.device)
    return com_ports

def try_connecting_to_ports(com_ports):
    for port in com_ports:
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            print(f"Connected to {port}")
            return ser
        except serial.SerialException:
            print(f"Failed to connect to {port}")
            continue
    return None

def search_and_connect():
    com_ports = find_com_ports()
    if not com_ports:
        print("No COM ports found.")
        return
    
    print(f"Found COM ports: {com_ports}")
    
    ser = try_connecting_to_ports(com_ports)
    if ser is None:
        print("Couldn't connect to any COM port.")
    else:
        return ser
    
# def light(light_level):
#     try:
#         int(light_level)
#     except TypeError:
#         print('{} not recognised. please enter int from 0-255'.format(light_level))
#         return
#     send_command()

    
# def interpret_move()

def main(COM=None, baudrate=115200, gcode=True):
    # command_list = [x for x in __dict__ functions]
    command_list = ['light']
    # command_dict = {'light': light}
    if COM is None:
        s = search_and_connect()
    else:
        s = serial.Serial(COM, 115200)# parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=1)
    s.flushInput()
    s.flushOutput()

    # s.write("a thing\r".encode())
    # mes = s.read_until().strip()
    # print(mes.decode())
    while True:
        com = get_input()
        com_split = com.split(' ')
        # if com_split[0] in command_list:
        if com_split[0] == 'light':
            try:
                light_level = int(com_split[1])
            except ValueError:
                print('Please enter an integer between 0 and 255')
                continue
            new_command = '*light {}'.format(light_level)
            send_command(s, new_command)
            

        if gcode:
            send_gcode(s, com)
        else:
            send_command(s, com)

def get_input():
    com = input('Enter Command: \n')
    return com

def send_command(ser, com):
    # ser.flushInput()
    ser.flushOutput()
    ser.write('{}\r'.format(com).encode())
    # mes = ser.read_until().strip()
    mes = ser.readline()
    print(mes.decode())

def send_gcode(ser, com, report=True):
    # ser.flushInput()
    # ser.flushOutput()

    ser.write((str(com)+'\n').encode())

    if report:
        start = time.time()
        while not ser.in_waiting:
            pass
        
        finish = time.time()
        difference = finish - start
        print(f"Waited {difference} seconds for response")
        
        # if ser.in_waiting:
        #     all_data = ser.read(ser.in_waiting).decode('utf-8')
        #     print(all_data)

        while ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            print(line)
    
    else:
        ser.flushOutput()

    # grbl_out = ser.readline() # Wait for grbl response with carriage return
    # print(grbl_out)
    # # print(grbl_out.decode())
    # try:
    #     print(grbl_out.decode('utf-8'))
    # except UnicodeDecodeError:
    #     print("Could not decode using UTF-8. Raw output:", grbl_out)

    # print(' : ' + str(grbl_out.strip()))

if __name__ == '__main__':
    main(COM='COM13')
    # main(COM='COM5')
    # main(COM='COM6')

#M106  - Fan on
#M107  - Fan off

#limits
#X axis - F10_000
#Y axis - F10_000
#Z axis = F5_000
