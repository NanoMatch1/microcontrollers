import os
import serial
import time

from controller import ArduinoUNO
from instruments import Instrument, Microscope, Camera, Spectrometer, StageControl, Monochromator, Laser, simulate
from calibration import ldrScans, Calibration
# from commands import CommandHandler, MicroscopeCommand, CameraCommand, SpectrometerCommand, StageCommand, MonochromatorCommand


def cli(instrument):
    while True:
        command = input("Enter a command: ")
        if command == 'exit':
            break

        if command == 'help':
            instrument.show_help()
            continue
    
        if command == 'debug':
            print("Debugging")
            breakpoint()
            
        result = instrument._command_handler(command)
        print(result)

class Interface:

    def __init__(self, simulate=False, debug_skip=[],  unoCOM='COM10', baud=9600):
        super().__init__(simulate=simulate)
        self.simulate = simulate
        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.scriptDir, 'data')
        self.transientDir = os.path.join(self.scriptDir, 'transient')
        self.saveDir = os.path.join(self.dataDir, 'saved_data')

        self.controller = ArduinoUNO()

        self.microscope = Microscope(self, simulate=simulate) # Microscope is a mediator
        self.camera = Camera(self, simulate=simulate)
        self.spectrometer = Spectrometer(self, simulate=simulate)
        self.stage = StageControl(self, simulate=simulate)
        self.monochromator = Monochromator(self, simulate=simulate)
        self.laser = Laser(self, simulate=simulate)

        self.command_map = self._generate_command_map()

        self._build_directories()
        self._generate_calibrations()

        self.grating_steps = None
        self.grating_wavelength = None
        self.laser_steps = None
        self.laser_wavelength = None
        self.triax_steps = None
        self.triax_wavelength = None

        self.current_wavelength = None
        self.current_shift = 0
        self.detector_safety = True

        self.acq_time = 1
        self.centre_wavelength = 376886
        self.filename = 'default'
        self.data = []

        self.flag_dict = {
            'S0': 'ok',
            'R1': 'motors running',
            'F0': 'invalid command',
            '#CF': 'end of response',
        }

        # These are all serial connections. In the future, we may establish all connections through the controller board, in which case only one connection command is required.
        if 'TRIAX' not in debug_skip:
            self.spectrometer.connect()
        if 'UNO' not in debug_skip:
            self.connect_to_controller(unoCOM, baud=9600)
        if not 'laser' in debug_skip:
            self.laser.connect()
        if not 'camera' in debug_skip:
            self.camera.connect()
            pass

        self._integrity_checker()

    
    def generate_help(self):
        help_dict = {}
        for command, (inst, method) in self.command_map.items():
            try:
                help_dict[str(inst)].append(f"{command} - {method.__doc__}")
            except KeyError:
                help_dict[str(inst)] = [f"{command} - {method.__doc__}"]
        return help_dict
    
    def show_help(self):
        help_dict = self.generate_help()
        print("Available commands:")
        for inst, commands in help_dict.items():
            print(f"{inst}:")
            for command in commands:
                print(f"   {command}")

    def _build_directories(self):
        '''Builds all the directories required for the system to run.'''

        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)
        if not os.path.exists(self.transientDir):
            os.makedirs(self.transientDir)
        if not os.path.exists(self.saveDir):
            os.makedirs(self.saveDir)

    def _generate_calibrations(self):
        self.calibrations = Calibration(self)

    def _generate_command_map(self):
        '''Dynamically generate a command map from the instruments declared in __init__'''
        instruments = [self.__getattribute__(attribute) for attribute in dir(self) if isinstance(self.__getattribute__(attribute), Instrument)]
        command_map = {
            funct: (instrument, method)
            for instrument in instruments
            for funct, method in instrument.command_functions.items()
        }
        return command_map

    def _command_handler(self, command:str):
        '''Handles the command and arguments passed to the Interface'''

        funct, args = self._command_parser(command)

        if funct in self.command_map:
            _, method = self.command_map[funct]
            result = method(*(args or []))
            return result
        else:
            return f" > Unknown command: {funct}"

         # Detail: * operator unpacks the list - since an empty list has nothing to unpack, nothing is passed to the function. This avoids a TypeError
    
    def _command_parser(self, command:str):
        tokens = [item.lower() for item in command.split(' ') if item != '']
        funct = tokens[0]
        if len(tokens) > 1:
            args = tokens[1:]
        else:
            args = []
        return funct, args

    def _integrity_checker(self):
        print("Microscope integrity check passed")
        pass

    @simulate(expected_value=serial.Serial)
    def connect_to_controller(self, unoCOM=None, baud=None):
        print('Connecting to microscope controller...')
        self.controller.connect(unoCOM, baud)
        print('Connected to microscope controller.')
        return self.serial.__class__



if __name__ == '__main__':
    instrument = Interface(simulate=True, unoCOM='COM10', debug_skip=['TRIAX', 'camera', 'laser'])
    cli(instrument)