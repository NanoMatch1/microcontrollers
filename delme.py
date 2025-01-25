import serial
import time

def connect_to_UNO(unoCOM='COM8', baud=9600):
    UNO_serial = serial.Serial(unoCOM, baud, timeout=1)
    while UNO_serial.in_waiting == 0:
        time.sleep(0.1)
    while UNO_serial.in_waiting > 0:
        response = UNO_serial.readline().decode().strip()
        print(response)
    return UNO_serial


test = connect_to_UNO()

