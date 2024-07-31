from machine import UART, Pin
import time
import rp2
from rp2 import PIO, StateMachine
import struct

# Define pins
test_rclk = Pin(22, Pin.OUT)
test_rclk.value(0)
count_enable_pin = Pin(6, Pin.OUT)
count_enable_pin.value(1)

GAL_1 = Pin(18, Pin.OUT)
GAU_2 = Pin(19, Pin.OUT)
GBL_3 = Pin(20, Pin.OUT)
GBU_4 = Pin(21, Pin.OUT)

# Function to convert an integer to bytes
def int_to_bytes(value, length):
    return value.to_bytes(length, 'big')

@rp2.asm_pio()
def counter_reader():
    """Read 8 bits from the pins and push to FIFO once, then halt."""
    in_(pins, 8)  # Read 10 bits of data
    push(block)    # Push the data to the FIFO
    return
#     mov(isr, null)  # Clear ISR (optional, for clarity)
#     mov(x, isr)  # Halt the state machine by moving a null value to X

def clear_fifo(sm):
    """Clear the FIFO by reading out all remaining entries."""
    print("clearing FIFO")
    while sm.rx_fifo():
        data = sm.get()
        print(data)
    print("finished clearing FIFO")
        

def setup_reader():
    """Setup the PIO State Machine to read 10 bits from specific pins."""
    sm = StateMachine(1, counter_reader, in_base=Pin(10), in_shiftdir=PIO.SHIFT_LEFT)  # Adjust in_base as needed
    sm.active(0)  # Ensure the state machine is initially inactive
    return sm

class APD_pico:
    def __init__(self, pin_read_order, rclk, monitor_pin=None, reset_pin=None, count_enable_pin=None, reader_sm=None, uart=None):
        self.monitor_pin = monitor_pin
        self.rclk = rclk
        self.count_enable_pin = count_enable_pin
        self.reader_sm = reader_sm
        self.uart = uart
        
        self.pin_read_order = pin_read_order
        self.acq_time = 1  # Acquisition time in seconds
        self.total_counts = 0
        
        for register in pin_read_order:
            register.value(1)

    def trigger_read(self):
        """Trigger a read on command, ensuring it reads only once."""
#         clear_fifo(self.reader_sm)  # Clear any old data from the FIFO
        self.reader_sm.active(1)  # Activate the state machine
#         time.sleep(0.00001)  # Short delay to ensure data is read (tune this as needed)
        self.reader_sm.active(0)  # Deactivate the state machine
#         self.sm_record_data()  # Read the data
#         clear_fifo(self.reader_sm)  # Clear the FIFO after reading

    

    def sm_record_data(self):
        """Read data from the state machine's FIFO."""
        while self.reader_sm.rx_fifo():
            result = self.reader_sm.get()  # Only call get if there is data
            print("claer")
        self.total_counts = result
        print("Data read from PIO:", result)
#         print("Finished FIFO read")
        
    def test_count_enable(self, value=0):
        self.count_enable_pin.value(value)
        return

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
        txData = b'UART-APD|UNO:#{}\n'.format(message)
        self.uart.write(txData)

    def send_custom_com(self, com):
        txData = b'{}\n'.format(com)
        self.uart.write(txData)

    def wait_for_uart(self):
        rxData = bytes()
        while True:
            check_uart = self.uart.any()
            if check_uart > 0:
                time.sleep(0.1)
                while self.uart.any() > 0:
                    rxData += self.uart.read(1)

                time.sleep(0.01)
                received = rxData.decode('utf-8').strip()
                return received
            else:
                time.sleep(0.01)

    def process_command(self, command, report=False):
        signal_direction = command[:command.index('#')]  # gets the signal direction
        command = command[command.index('#') + 1:]  # removes the coms directionality from the UART signal
        command = command.split(' ')
#         print(command)
        if command[0] == 'echo':
            self.send_UART('polo')
        if command[0] == '':
            return None
        if command[0] == 'ce':  # tests the counting enable pin electronics
            if len(command) > 1:
                try:
                    value = int(command[1])
                except Exception as e:
                    print('error on ce line')
                    print(e)
            else:
                value = 0

            print('setting test enable to {}'.format(value))
            self.test_count_enable(value)
            return
        
        if command[0] == 'read':
            self.rclk.value(1)
            self.count_int_list = []
            
            for register in self.pin_read_order:
                print('Reading from register 1, {}'.format(register))
                self.total_counts = 0
                register.value(0)
                self.trigger_read()
                register.value(1)
                self.sm_record_data()
#                 register.value(1)
                
                print("Read {}".format(self.total_counts))
                print(bin(self.total_counts))
                
                
                self.count_int_list.append(self.total_counts)
            
        self.rclk.value(0)
        print(self.count_int_list)
        newByteList = b''.join([int_to_bytes(byteval, 1) for byteval in self.count_int_list]) # the order of the byte is little-endian
        print(newByteList)
        integer_value = int.from_bytes(newByteList, 'little') # the order is little-endian
        print(integer_value)
        # Convert the byte sequence to a 32-bit integer
#         if len(newByteList) == 4:
#             integer_value = struct.unpack('>I', newByteList)[0]
#             print("32-bit Integer Value:", integer_value)
#             print("Hex Integer Value:", hex(integer_value))
#         else:
#             print("Error: Byte list does not contain exactly 4 bytes.")

#         newByte = 0x00
#         integer_value = struct.unpack('>I', newByteList)[0]
#         for byte_value self.newByteList:
#             newByte = (byte_value << 8) | byte_value
                
        print('Successfully read from registers. {}'.format(integer_value))
        self.send_UART("full_integer: {}".format(integer_value))

        if command[0] == 'test':
            self.total_counts = 0  # Reset count at the start of acquisition
            self.reset_pin.value(1)
            time.sleep(0.00001)
            self.reset_pin.value(0)

            # Start acquiring
            start_time = time.ticks_us()
            self.count_enable_pin.value(0)

            while time.ticks_diff(time.ticks_us(), start_time) < self.acq_time * 1000000:
                pass  # Continue to count in the background via interrupt

            self.count_enable_pin.value(1)
            stop_time = time.ticks_us()

            self.trigger_read()
            self.sm_record_data()

            total_time = time.ticks_diff(start_time, stop_time)
            print("total time: {}".format(total_time))
            print("total counts: {}".format(self.total_counts))
            time_avg = self.total_counts / total_time
            print("time-averaged counts: {}".format(time_avg))

            self.send_UART("total time: {}".format(total_time))
            self.send_UART("total counts: {}".format(self.total_counts))
            self.send_UART("time-averaged counts: {}".format(time_avg))

#             clear_fifo(self.reader_sm)
            self.total_counts = 0
            
#             self.trigger_read()
#             self.sm_record_data()

        elif command[0] == 'time':
            self.acq_time = float(command[1])
            self.send_UART('Acquisition time set to {}'.format(self.acq_time))

        elif command[0] == 'acq':
            if len(command) > 1:
                try:
                    self.acq_time = float(command[1])
                except ValueError:
                    print('{} not recognized as a number. Please enter a number from 0-100'.format(command[1]))

            total_counts = self.acquire_signal()
            self.send_custom_com('#DAT{}'.format(total_counts))
            return total_counts

        elif command[0].strip() == 'run':
            if len(command) > 1:
                try:
                    self.acq_time = float(command[1])
                except ValueError:
                    print('{} not recognized as a number. Please enter a number from 0-100'.format(command[1]))

            self.send_UART('Running for 30 seconds')
            count = 0

            while count < 30 / self.acq_time:
                total_counts = self.acquire_signal()
                self.send_UART(total_counts)
                count += 1
            self.send_UART('Finished running')

        elif command[0].strip() == 'runlong':
            if len(command) > 1:
                try:
                    self.acq_time = float(command[1])
                except ValueError:
                    print('{} not recognized as a number. Please enter a number from 0-100'.format(command[1]))

            self.send_UART('Running for 30 seconds')
            count = 0

            while count < 120 / self.acq_time:
                total_counts = self.acquire_signal()
                self.send_UART(total_counts)
                count += 1
            self.send_UART('Finished running')

        else:
            print('received command {}'.format(command))
            self.send_UART('"{}" not recognised as a command. No action performed'.format(' '.join(command)))

    def acquire_signal(self, acq_time=None):
        if acq_time:
            self.acq_time = acq_time
        self.total_counts = 0  # Reset count at the start of acquisition

        start_time = time.ticks_us()

        while time.ticks_diff(time.ticks_us(), start_time) < self.acq_time * 1000000:
            self.reset_pin.value(1)
            self.reset_pin.value(0)
            self.sm_record_data()
            pass  # Continue to count in the background via interrupt

        return self.total_counts

    def sm_single_test(self):
        self.reset_pin.value(1)
        self.reset_pin.value(0)

        if self.reader_sm.rx_fifo():
            result = self.reader_sm.get()  # Only call get if there is data
            self.total_counts += result
        else:
            pass

    def intensity_calibration(self, run_time=30, acq_time=0.1):
        data_list = []
        count = 0
        self.acq_time = acq_time
        while count < run_time / acq_time:
            intensity = self.acquire_signal()
            self.send_UART(intensity)
            count += 1

def main():
    # Configure the reader state machine
    reader_sm = setup_reader()

    # Configure UART
    uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

    # Instantiate APD_pico class
    APD = APD_pico([GAL_1, GAU_2, GBL_3, GBU_4], test_rclk, count_enable_pin=count_enable_pin, reader_sm=reader_sm, uart=uart1)

    # Main loop
    while True:
        try:
            command = APD.wait_for_uart()
            if command == "trigger_read":
                APD.trigger_read()
            else:
                APD.process_command(command)
        except Exception as e:
            print("command processing error:", e)

if __name__ == "__main__":
    main()



