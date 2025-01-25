import os

from functools import wraps
from instruments import Microscope, Camera, Spectrometer, Stage, Monochromator
from commands import CommandHandler, MicroscopeCommand, CameraCommand, SpectrometerCommand, StageCommand, MonochromatorCommand

def simulate(expected_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.simulated:
                return expected_value
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


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
        self.stage = Stage()
        self.monochromator = Monochromator()
        
        self.function_map = {
            'microscope': self.microscope.command_functions.keys(),
            'camera': self.camera.command_functions.keys(),
            'spectrometer': self.spectrometer.command_functions.keys(),
            'stage': self.stage.command_functions.keys(),
            'monochromator': self.monochromator.command_functions.keys()           
        }


        self._integrity_checker()

    def _command_handler(self, funct, args):
        for instrument, commands in self.function_map.items():
            if funct in commands:
                response = self.__getattribute__(instrument).command_functions[funct](*(args or []))
                return response
        # * operator unpacks the list - since an empty list has nothing to unpack, nothing is passed to the function. This avoids a TypeError
    
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
    breakpoint()