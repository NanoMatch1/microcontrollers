from machine import UART
import time
import sys
import select
from machine import UART, Pin
import time

uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# USB serial setup
def wait_for_command(echo = False ):
    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.readline()
            command = ch.strip()
            if command[0] == 'a':
                try:
                    acq_time = float(command[1:])
                except TypeError:
                    print("Error - {} not recognised as a time. Please enter a float or int.".format(command[1:]))
                
                print('aa{}'.format(acq_time))

            return command
        else:
            time.sleep(0.01)
            continue

while True:
    try:
        processed = wait_for_command()
    except Exception as e:
        print(e)
#     print(command)
#     command = None
    time.sleep(1)
#     sys.stdin.flush()
    continue
    txData = b'{}\n\r'
#     print('writing to UART')
#     uart.write(b"{}\n".format(command))   # Send command to Pico B via UART
    uart0.write(txData)
    time.sleep(0.1)

    rxData = bytes()

    while uart0.any() == 0:
        time.sleep(0.1)
        continue

        while uart0.any() > 0:
            rxData += uart0.read(1)

        time.sleep(0.01)
    #     output = 'UART_out'
        received = rxData.decode('utf-8')
        print(received)
        break

