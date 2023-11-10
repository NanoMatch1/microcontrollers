from machine import UART, Pin
import time
import sys
import select

while True:
    if select.select([sys.stdin],[],[],0)[0]:
        ch = sys.stdin.readline()
        ch = ch.strip()
        print(ch)
        if ch == 'do':
            print('command recognised as "do"')
    else:
        pass

    time.sleep(0.01)