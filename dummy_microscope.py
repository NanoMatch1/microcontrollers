import os

from commands import CommandHandler, MicroscopeCommand, CameraCommand, SpectrometerCommand, StageCommand, MonochromatorCommand

class DummyInstrument:

    def __init__(self):
        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.scriptDir, 'data')
        self.transientDir = os.path.join(self.scriptDir, 'transient')
        self.saveDir = os.path.join(self.dataDir, 'saved_data')

        self.command_handler = CommandHandler()
        self._integrity_checker()

    def _integrity_checker(self):
        print("Microscope integrity check passed")
        pass


if __name__ == '__main__':
    instrument = DummyInstrument()
    breakpoint()