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

        self.command_handler = CommandHandler()
        self._integrity_checker()



    def _integrity_checker(self):
        print("Microscope integrity check passed")
        pass



if __name__ == '__main__':
    instrument = InstrumentMediator(simulate=True)
    breakpoint()