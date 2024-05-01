import gpib_ctypes
import pyvisa
import time
# import serial

'''# looking for some kind of response like "b" or "o". Use command "O2000" to enter into command mode.
Initial grating is Blaze 500, 1200 g/mm
centre for 532 nm is roughly 241543
List of useful commands = {
"Initiate command mode": "02000",
# "Initialise Spectrometer: "A",
"read motor position": "H0",
"read slit position: "j0,0",
"move slit relative: "k0,0,100"
"poll motors after move command sent - necessary because control is given to PC immediately after command is given, but new motor command cannot be issued until motor motion is stopped. Implement a check for this here. Note if the motors are not busy, a timeout is received... could be a delay/timing issue: "E",
"move exit mirror to front exit (out of path): "f0".
"move exit mirror to side exit (in path): "e0",
"entrance mirror to front enterance: "c0",
"entrance mirror to side enterance: "d0"


'''

class Microscope:

    def __init__(self):
        self.spectrometer_dict = {
            'init': 'A',
            'comsmode': '02000',
            'read_grating': 'H0',
            'grating': 'F0,',
            'read_enter': 'j0,0',
            'move_enter': 'k0,0,',
            'move_exit': 'k0,3,',
            'poll motors after move command sent': 'E',
            'ccd_mode': 'f0',
            'apd_mode': 'e0'
            #'entrance mirror to front enterance': 'c0',
            #'entrance mirror to side enterance': 'd0'
        }
        self.pico_dict = {
            'X': 'X',
            'Y': 'Y',
            'Z': 'Z'
        }

        self.spectrometer, self.state = self.connect_to_spectrometer()
        

    def connect_to_spectrometer(self):
        # Open a connection to the instrument
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        spectrometer = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument

        spectrometer.write('WHERE AM I')
        time.sleep(0.0001)
        state = spectrometer.read()
        print(state)
        # breakpoint()
        return spectrometer, state


    def main(self):
        while True:
            try:
                # loop continuously here for com input
                com = input('Enter command:\n')
                # if com == 'COM':
                #     while True:
                #         com = 'Enter string command:\n'
                #         # self.instrument.write(com)
                #         # time.sleep(0.0001)
                # else:
                command = com.split(' ')
                if command[0] in self.spectrometer_dict.keys():
                    # self.instrument.write(com)
                    # time.sleep(0.0001)
                    if len(command) > 1:
                        command = '{}{}'.format(self.spectrometer_dict[command[0]], command[1]) # concatenate command if parameters are provided
                    else:
                        command = self.spectrometer_dict[command[0]]
                    self.spectrometer.write(command)
                    # self.spectrometer.write(com)
                if com == 'init':
                    count = 100
                    while count > 0:
                        print('Initialising: Sleeping for {} seconds'.format(count))
                        time.sleep(1)
                        count -= 1
                response = self.spectrometer.read()
                print('RES:', response)
            except Exception as e:
                print(e) 

                    
            except Exception as e:
                print(e)

if __name__ == '__main__':
    microscope = Microscope()
    microscope.main()

# class Spectrometer:

    def __init__(self):
        self.spectrometer, spectrometer_state = self.connect_to_spectrometer()

    def connect_to_spectrometer(self):
        # Open a connection to the instrument
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        spectrometer = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument
        # instrument = rm.open_resource('COM6')  # Replace with the actual VISA address of your instrument
        # s = serial.Serial(port='GPIB0::1::INSTR', timeout=5000)


    # def connect(instrument):
        spectrometer.write('WHERE AM I')
        time.sleep(0.0001)
        state = spectrometer.read()
        print(state)
        # breakpoint()
        return spectrometer, state





    def control_instrument(self, command):
        while True:
            try:
                # loop continuously here for com input
                com = input('Enter command - c to continue:\n')
                if com == 'c':
                    break
                spectrometer.write(com)
                if com == 'A':
                    count = 100
                    while count > 0:
                        print('Initialising: Sleeping for {} seconds'.format(count))
                        time.sleep(1)
                        count -= 1
                response = spectrometer.read()
                print('RES:', response)
            except Exception as e:
                print(e) 

        count = 0
        for x in range(10):
            spectrometer.write('F0,{}'.format(5000))
            response = spectrometer.read()
            print('moving to {}'.format(x*5000))
            # while response == 'b':
            # while True:
            #     # response = spectrometer.write('E')
            #     time.sleep(0.5)
            #     count+=1
            #     if count > 50:
            #         break
            time.sleep(0.5)
            # count += 1
                # print('waiting')
                
                # response = spectrometer.read()
                # if count > 50:
                #     print('timed out')
                #     break

            

            
            

        while True:
            try:
                com = input('Enter command:\n')
                spectrometer.write(com)
                response = spectrometer.read()
                print('RES:', response)
            except Exception as e:
                print(e) 
                

        breakpoint()
        # Read the response from the spectrometer

        try:
            response = spectrometer.read()
            print("Response:", response)
        except pyvisa .VisaIOError as e:
            if e.error_code == pyvisa.constants.VI_ERROR_TMO:
                print("Timeout expired. spectrometer did not respond.")
            else:
                print("An error occurred:", e)


        # Close the spectrometer connection
        spectrometer.close()


        #k0,0,100 = move slit 100 steps relative
        #j0,0<CR> = read slit pos
        #i0,0,0<CR> = set slit position (0)
