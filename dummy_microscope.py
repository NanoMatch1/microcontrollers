import os

from commands import MicroscopeCommand, CameraCommand, SpectrometerCommand, StageCommand, MonochromatorCommand

class CommandHandler:

    def __init__(self):
        self.handle_microscope = MicroscopeCommand()
        self.handle_camera = CameraCommand()
        self.handle_spectrometer = SpectrometerCommand()
        self.handle_stage = StageCommand()
        self.handle_monochromator = MonochromatorCommand()

    def __call__(self, *args, **kwds):
        return self.parse_command()

    def extract_tokens(self, command):
        tokens = [item.lower() for item in command.split(' ')]
        return tokens

    def parse_command(self, command):
        tokens = self.extract_tokens(command)
        keyword = tokens[0]

        if keyword in self.handle_microscope.command_functions.keys():
            return self.handle_microscope(tokens)
        elif self.command in self.camera_dict:
            return self.handle_camera(tokens)
        elif self.command in self.spectrometer_dict:
            return self.handle_spectrometer(tokens)
        elif self.command in self.stage_dict:
            return self.handle_stage(tokens)
        elif self.command in self.monochromator_dict:
            return self.handle_monochromator(tokens)
        else:
            return None
        

class DummyMicroscope:

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
    microscope = DummyMicroscope()
    breakpoint()