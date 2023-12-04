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
