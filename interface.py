import os

from functools import wraps
from instruments import Instrument, Microscope, Camera, Spectrometer, StageControl, Monochromator
# from commands import CommandHandler, MicroscopeCommand, CameraCommand, SpectrometerCommand, StageCommand, MonochromatorCommand

def simulate(expected_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.simulated:
                return expected_value
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

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
            for instrument, commands in help_dict.items():
                print(f"{instrument}:")
                for command in commands:
                    print(f"   {command}")
            continue
            
        result = instrument._command_handler(*instrument._command_parser(command))
        print(result)

class InstrumentMediator:

    def __init__(self, simulate=False):
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

        self.command_map = self._generate_command_map()

        self._integrity_checker()

    def _generate_command_map(self):
        '''Dynamically generate a command map from the instruments declared in __init__'''
        instruments = [self.__getattribute__(attribute) for attribute in dir(self) if isinstance(self.__getattribute__(attribute), Instrument)]
        command_map = {
            funct: (instrument, method)
            for instrument in instruments
            for funct, method in instrument.command_functions.items()
        }
        return command_map

    def _command_handler(self, funct, args):
        if funct in self.command_map:
            _, method = self.command_map[funct]
            result = method(*(args or []))
            return result
        print(f"Unknown command: {funct}")

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
    instrument = InstrumentMediator(simulate=True)
    cli(instrument)