import inspect
from abc import ABC, abstractmethod

from instruments import Microscope, Camera, Spectrometer, Stage, Monochromator

def ui_callable(func):
    """
    Decorator that marks a method as UI-callable by
    setting a custom attribute on the function object.
    """
    func.is_ui_process_callable = True
    return func



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
        


class Command(ABC):
    def __init__(self):
        self.command_functions = {}

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Subclasses handle how commands are invoked.
        """
        pass

    def _integrity_checker(self):
        """
        Checks that every UI-callable method is in command_functions
        and that every command_functions entry is actually UI-callable.
        """

        # 1) Gather all methods (bound or unbound) decorated with @ui_callable
        ui_callable_methods = set()
        # Because we want bound methods for the instance, we use `inspect.ismethod`.
        # That ensures we get `self.run_scan_spectrum` bound to `self`, etc.
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, 'is_ui_process_callable', False):
                ui_callable_methods.add(method)

        # 2) Gather all methods that appear in your command_functions dict
        cmd_methods = set(self.command_functions.values())

        # 3) Compare them
        if ui_callable_methods != cmd_methods:
            # This means at least one UI-callable method is missing
            # from self.command_functions or vice versa.
            missing_in_dict = ui_callable_methods - cmd_methods
            missing_in_ui = cmd_methods - ui_callable_methods

            message = []
            if missing_in_dict:
                message.append(
                    f"These @ui_callable methods are not in command_functions: "
                    f"{[m.__name__ for m in missing_in_dict]}"
                )
            if missing_in_ui:
                message.append(
                    f"These methods in command_functions are not decorated with @ui_callable: "
                    f"{[m.__name__ for m in missing_in_ui]}"
                )
            raise ValueError("\n".join(message))

        print(f"{self.__class__} integrity check passed")

