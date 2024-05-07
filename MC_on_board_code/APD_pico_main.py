from machine import UART, Pin
import time
import rp2
from rp2 import PIO, StateMachine

# # Global variable to store counts
# total_count = 0

# Pin connected to the 10th bit of your external counter
monitor_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # Adjust pin number as needed
reset_pin = Pin(22, Pin.OUT)
reset_pin.value(0)

@rp2.asm_pio()
def counter_reader():
    """Read 8 bits from the pins and push to FIFO."""
    wait(1, pin, 0)   # Wait for pin to be high indicating data ready (adjust as needed)
    in_(pins, 10)       # Read 8 bits of data
    push(block)        # Push the data to the FIFO

def setup_reader():
    """Setup the PIO State Machine to read 8 bits from specific pins."""
    sm = StateMachine(1, counter_reader, in_base=Pin(10), in_shiftdir=PIO.SHIFT_LEFT)  # Adjust in_base as needed
    sm.active(1)  # Ensure the state machine is active
    return sm

def calibration_test(APD, time_list = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8], repeats = 5, filename = "output"):
    
    data_list = []
    for xtime in time_list:
        idx = 0
        while idx < repeats:
            counts = APD.acquire_signal(xtime)
            data_list.append([xtime, counts])
            idx += 1
            
    print("calibration complete:\n", data_list)
    save_2d_list_as_txt(data_list, "{}.txt".format(filename))
    return data_list


        
def save_2d_list_as_txt(data, filename):
    with open(filename, 'w') as file:
        for row in data:
            file.write(','.join(str(item) for item in row) + '\n')
            

    
class APD_pico:
    
    def __init__(self, **kwargs):

        self.__dict__.update(kwargs)

        for argument in ['monitor_pin', 'reset_pin', 'reader_sm', 'uart']:
            if argument not in kwargs:
                raise ValueError('{} is a required argument'.format(argument))
            
        self.acq_time = 1 # acquistion time in seconds
        self.total_counts = 0
        
    def receive_UART(self):
        rxData = bytes()
        while True:
            if self.uart.any() == 0:
                time.sleep(0.01)
                continue
            while self.uart.any() > 0:
                rxData += self.uart.read(1)

            time.sleep(0.01)
            # decodes UART command into a string
            command = rxData.decode('utf-8')
            return command
        
    def send_UART(self, message):
        txData = b'UART_APD|B:{}'.format(message)
        self.uart.write(txData)

    def wait_for_command(self):
        command = self.receive_UART()
        return command


    def process_command(self, command):
        command = command.split(' ')
        if command[0] == 'time':
            self.acq_time = float(command[1])
            self.send_UART('Acquisition time set to {}'.format(self.acq_time))

        if command[0] == 'acq':
            if len(command) > 1:
                try:
                    self.acq_time = float(command[1:])

                except ValueError:
                    print('{} not recognized as a number. Please enter a number from 0-100'.format(command[1]))

            self.send_UART('Acquiring signal for {} seconds'.format(self.acq_time))
            total_counts = self.acquire_signal()
            return total_counts
        
        if command[0].strip() == 'run':
            self.send_UART('Running for 30 seconds')
            for _ in range(30):
                total_counts = self.acquire_signal()
                self.send_UART(total_counts)

    def acquire_signal(self, acq_time = None):
        if acq_time:
            self.acq_time = acq_time
        # duration in seconds
        self.total_counts = 0  # Reset count at the start of acquisition

        # Start acquiring
        start_time = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), start_time) < self.acq_time * 1000000:
            self.sm_record_data()
            pass  # Continue to count in the background via interrupt

        # Duration has passed, print the total count
        # print("Total counts:", total_count)
        return self.total_counts
    
    def sm_record_data(self):
        # reset counter - #CHECK whether we perform this first or dead from the FIFO first...
        self.reset_pin.value(1)
        self.reset_pin.value(0)
        
        if self.reader_sm.rx_fifo():
            result = self.reader_sm.get()  # Only call get if there is data
            total_count += result
            #print("Data read from PIO:", result)
        else:
            pass
            #print("No data available in FIFO")

    def intensity_calibration(self, run_time = 30, acq_time = 0.1):
        data_list = []
        count = 0
        self.acq_time = acq_time
        while count < run_time/acq_time:
            intensity = self.acquire_signal()
            self.send_UART(intensity)
            count += 1
            


def main():
    # Configure interrupt for the pin on both edges (assuming you need both)
    reader_sm = setup_reader()
    reader_sm.active(1)
    #monitor_pin.irq(trigger=Pin.IRQ_RISING, handler=bit_flip_handler)
    # configure UART
    uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

    APD = APD_pico(monitor_pin = monitor_pin, reset_pin = reset_pin, reader_sm = reader_sm, uart = uart0)

    # sm_record_data(reset_pin, reader_sm)
    while True:
        command = APD.wait_for_command()
        try:
            result = APD.process_command(command)
        except Exception as e:
            print('Command Process Error:\n{}'.format(e))
        print(result)
