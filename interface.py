import os

from instruments import Instrument, Microscope, Camera, Spectrometer, StageControl, Monochromator, Laser, simulate
from calibration import ldrScans, Calibration
# from commands import CommandHandler, MicroscopeCommand, CameraCommand, SpectrometerCommand, StageCommand, MonochromatorCommand

def generate_help_dict(instrument):
    help_dict = {}
    for command, (inst, method) in instrument.command_map.items():
        try:
            help_dict[str(inst)].append(f"{command} - {method.__doc__}")
        except KeyError:
            help_dict[str(inst)] = [f"{command} - {method.__doc__}"]
    return help_dict

def cli(instrument):
    while True:
        command = input("Enter a command: ")
        if command == 'exit':
            break

        if command == 'help':
            print("Available commands:")
            help_dict = generate_help_dict(instrument)
            for inst, commands in help_dict.items():
                print(f"{inst}:")
                for command in commands:
                    print(f"   {command}")
            continue
            
        result = instrument._command_handler(command)
        print(result)

class InstrumentMediator:

    def __init__(self, simulate=False, debug_skip=[], unoCOM='COM8'):
        self.simulate = simulate
        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.scriptDir, 'data')
        self.transientDir = os.path.join(self.scriptDir, 'transient')
        self.saveDir = os.path.join(self.dataDir, 'saved_data')

        self.microscope = Microscope()
        self.camera = Camera()
        self.spectrometer = Spectrometer()
        self.stage = StageControl()
        self.monochromator = Monochromator()
        self.laser = Laser()

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

        if 'TRIAX' not in debug_skip:
            self.spectrometer, self.state = self.connect_to_triax()
        if 'UNO' not in debug_skip:
            self.uno_serial = self.connect_to_UNO(unoCOM, baud=9600)
        if not 'laser' in debug_skip:
            self.laser_serial = self.connect_to_laser()
        if not 'camera' in debug_skip:
            # self.camera = PIXISCam(self)
            self.camera = Camera()
            pass

        self._integrity_checker()

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
        '''Handles the command and arguments passed to the InstrumentMediator'''

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



if __name__ == '__main__':
    instrument = InstrumentMediator(simulate=True, debug_skip=['TRIAX', 'camera', 'laser'])
    cli(instrument)