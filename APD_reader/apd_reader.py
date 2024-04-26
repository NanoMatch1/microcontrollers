from machine import I2C, Pin, Timer
import time
import rp2
from rp2 import PIO, StateMachine

# Global variable to store counts
total_count = 0

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

def acquire_signal(duration, reset_pin, reader_sm):
    # duration in seconds
    global total_count
    total_count = 0  # Reset count at the start of acquisition

    # Start acquiring
    start_time = time.ticks_us()
    while time.ticks_diff(time.ticks_us(), start_time) < duration * 1000000:
        sm_record_data(reset_pin, reader_sm)
        pass  # Continue to count in the background via interrupt

    # Duration has passed, print the total count
    print("Total counts:", total_count)
    return total_count

#def bit_flip_handler(pin):
#    global total_count
#    # Reset the external hardware counter here if needed
#    reset_pin.value(1)
#    reset_pin.value(0)
#    # Increment the internal count
#    total_count += 1


# Function to handle I2C communication
def i2c_handler():
    global total_count
    while True:
        if i2c.any():  # Check if there is a read request
            message = i2c.readfrom(0x12, 4)  # Assuming address and size
            if message == b'read':
                # Respond with the current count
                i2c.writeto(0x12, str(total_count))

# Example usage of the I2C handler in your main function or as a separate thread
# i2c_handler()  # Call this in your main loop or setup as needed
def calibration_test(time_list = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8], repeats = 5, filename = "output"):
    
    data_list = []
    for xtime in time_list:
        idx = 0
        while idx < repeats:
            counts = acquire_signal(xtime)
            data_list.append([xtime, counts])
            idx += 1
            
    print("calibration complete:\n", data_list)
    save_2d_list_as_txt(data_list, "{}.txt".format(filename))
    return data_list

def intensity_calibration(reset_pin, reader_sm, time = 30):
    data_list = []
    count = 0
    while count < time*10:
        intensity = acquire_signal(0.1, reset_pin, reader_sm)
#        print(intensity)
        count += 1
        
        
def save_2d_list_as_txt(data, filename):
    with open(filename, 'w') as file:
        for row in data:
            file.write(','.join(str(item) for item in row) + '\n')
            
def sm_record_data(reset_pin, reader_sm):
    global total_count
    # reset counter
    reset_pin.value(1)
    reset_pin.value(0)
    
    if reader_sm.rx_fifo():
        result = reader_sm.get()  # Only call get if there is data
        total_count += result
        #print("Data read from PIO:", result)
    else:
        pass
        #print("No data available in FIFO")
        
    

def main():
    # Configure interrupt for the pin on both edges (assuming you need both)
    reader_sm = setup_reader()
    reader_sm.active(1)
    #monitor_pin.irq(trigger=Pin.IRQ_RISING, handler=bit_flip_handler)


# Setup I2C
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)  # Configure pins as per your setup
    #reader_sm = setup_reader()
    #reader_sm.active(1)
    
    print("about to record count")
    #result = reader_sm.get()
    sm_record_data(reset_pin, reader_sm)
    #print(result)
    print("finished reading result")

    while True:
        com = input("Enter acquistion time: ")
            #duration = float(input("Enter the duration for signal acquisition in seconds: "))
        if com == "test":
            filename = input("enter a filename: ")
            if filename == '':
                filename = "output"
            calibration_test(filename = filename)
            continue
        elif com == "int":
            intensity_calibration(reset_pin, reader_sm)
            continue
        try:
            duration = float(com)
            acquire_signal(duration, reset_pin, reader_sm)
            
        except ValueError:
            print("Invalid input! Please enter a valid number.")
# Run the main function if this script is executed as the main program
if __name__ == "__main__":
    main()



