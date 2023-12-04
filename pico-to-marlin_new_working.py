# from machine import UART, Pin, USB_VCP
# import utime
# import time
# import serial
# # Replace with your serial port and baud rate
# serial_port = 'COM5'  # or 'COM3' for Windows
# baud_rate = 115200  # Adjust as per your Pico's settings
# read_delay = 0.1  # This is important! Some Picos need a delay before sending data
# # Initialize USB serial for computer communication
# usb = USB_VCP()

# # Initialize UART0 for 3D printer communication
# uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# # Initialize UART1 for computer communication
# uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

# def send_gcode(command):
#     command += '\n'
#     uart0.write(command)

#     # Read and print the response from 3D printer to computer via UART1 and USB (optional)
#     if uart0.any():
#         response = uart0.readline()
#         uart1.write("Received: " + response.decode('utf-8'))
#         usb.write("Received: " + response.decode('utf-8'))


# try:
#     # Establish a serial connection
#     # ser = serial.Serial(serial_port, baud_rate, timeout=1)
#     if uart1.any():
#         command_from_computer = uart1.readline().decode('utf-8').strip()
#         print(command_from_computer)
#         breakpoint()
#         send_gcode(command_from_computer)
        
#     # Check if data is available from the computer via USB
#     if usb.any():
#         command_from_usb = usb.readline().decode('utf-8').strip()
#         send_gcode(command_from_usb)

#     utime.sleep(0.1)
#     ser.flushInput()
#     ser.flushOutput()
#     while True:
#         # Send a command
#         inp = input('Enter command: ')
#         ser.write(f'{inp}\n\r'.encode())

#         # Read the response
#         response = ser.read(ser.inWaiting())  # Read available bytes
#         if response:
#             print("Response from Pico:")
#             print(response.decode().strip())
#         else:
#             print("No response received. Check the connection and settings.")

# except serial.SerialException as e:
#     print(f"Error: {e}")


import serial
import time

# Replace with your serial port and baud rate
serial_port = 'COM5'  # or 'COM3' for Windows
baud_rate = 115200  # Adjust as per your Pico's settings
read_delay = 0.1  # This is important! Some Picos need a delay before sending data

try:
    # Establish a serial connection
    ser = serial.Serial(serial_port, baud_rate, timeout=1) 
    ser.flushInput()
    ser.flushOutput()
    while True:
        # Send a command
        inp = input('Enter command: ')
        ser.write(f'{inp}\n\r'.encode())

        # Read the response
        response = ser.read(ser.inWaiting())  # Read available bytes
        if response:
            print("Response from Pico:")
            print(response.decode().strip())
        else:
            print("No response received. Check the connection and settings.")
except serial.SerialException as e:
    print(f"Error: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
