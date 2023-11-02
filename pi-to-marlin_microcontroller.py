from machine import UART, Pin, USB_VCP
import utime

# Initialize USB serial for computer communication
usb = USB_VCP()

# Initialize UART0 for 3D printer communication
uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Initialize UART1 for computer communication
uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

def send_gcode(command):
    command += '\n'
    uart0.write(command)

    # Read and print the response from 3D printer to computer via UART1 and USB (optional)
    if uart0.any():
        response = uart0.readline()
        uart1.write("Received: " + response.decode('utf-8'))
        usb.write("Received: " + response.decode('utf-8'))

while True:
    # Check if data is available from the computer via UART1
    if uart1.any():
        command_from_computer = uart1.readline().decode('utf-8').strip()
        send_gcode(command_from_computer)
        
    # Check if data is available from the computer via USB
    if usb.any():
        command_from_usb = usb.readline().decode('utf-8').strip()
        send_gcode(command_from_usb)

    utime.sleep(0.1)
