import serial
import time

ser = serial.Serial('COM11', 115200)  # Change ttyUSB0 to your actual port
time.sleep(2)  # Give time for serial connection to initialize

while True:
    command = input("Enter G-code command: ")
    ser.write((command + '\n').encode())
    
    # Read response from Raspberry Pi Pico
    # time.sleep(0.1)
    while not ser.in_waiting:
        time.sleep(0.001)
    while ser.in_waiting:
        print(ser.readline().decode().strip())
p