import inspect
from abc import ABC, abstractmethod

def ui_callable(func):
    """
    Decorator that marks a method as UI-callable by
    setting a custom attribute on the function object.
    """
    func.is_ui_process_callable = True
    return func




class Instrument(ABC):
    def __init__(self):
        self.command_functions = {}

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



class Microscope(Instrument):



        # 'scan_min': self.set_scan_min,
        # 'scan_max': self.set_scan_max,
        # 'scan_res': self.set_scan_resolution,
        # 'acq_time': self.set_acquisition_time,
        # 'sl': self.go_to_laser_wavelength,
        # 'sd': self.go_to_grating_wavelength,
        # 'st': self.go_to_triax_wavelength,
        # 'sall': self.go_to_wavelength_all,
        # 'wai': self.get_all_current_positions,
        # 'reference': self.reference_calibration, # TODO: Bug where multiple calls are needed to refresh. Looks like grating motors are one step behind.
        # 'shift': self.go_to_wavenumber,
        # 'calshift': self.simple_calibration_shift,
        # 'isrun': self.wait_for_motors,
        # 'report': self.report_status,
        # 'setmode': self.change_monochromator_mode,
        # 'writemotora': self.set_absolute_positions_A,
        # 'writemotorb': self.set_absolute_positions_B,
        # 'help': self.show_help,
        # 'motorscan': self.motor_scan,
        # 'lockcal': self.lock_calibration,
        # 'unlockcal': self.unlock_calibration,
        # 'pin': self.move_pinhole,
        # 'setpin': self.set_pinhole_pos,
        # 'mshut': self.close_mono_shutter,
        # 'mopen': self.open_mono_shutter,
        # 'readldr': self.read_ldr0,
        # 'debug': self.print_debug,
        # 'calibrate': self.run_calibration,
        # 'gtgsteps': self.go_to_grating_steps,
        # 'homemono': self.home_motors_monochromator,
        # 'camera': self.start_camera_ui, # for testing
        # 'pixelcal': self.calibrate_triax_pixels,
        # 'acquire': self.acquire_spectrum,
        # 'run': self.continuous_acquire,
        # 'stop': self.stop_continuous_acquire,

    def __init__(self):
        super().__init__()
        # Suppose you have two UI-callable methods below.
        self.command_functions = {
            'scan': self.run_scan_spectrum,
            'get_grating_position': self.get_grating_position,
            'set_scan_min': self.set_scan_min,
        }

        self._integrity_checker()  # Validate on init

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown command: '{command}'")
        return self.command_functions[command](*args, **kwargs)

    @ui_callable
    def run_scan_spectrum(self):
        print('Scanning spectrum...')
        return True
    
    @ui_callable
    def get_grating_position(self):
        print('Getting grating position...')
        return 356465

    @ui_callable
    def set_scan_min(self):
        print('Setting scan minimum...')

class Camera(Instrument):
    def __init__(self):
        super().__init__()
        self.command_functions = {
            'capture': self.capture_frame
        }

        self._integrity_checker()

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown camera command: '{command}'")
        return self.command_functions[command](*args, **kwargs)

    @ui_callable
    def capture_frame(self):
        print("Capturing a frame from the camera.")

class Spectrometer(Instrument):
    def __init__(self):
        super().__init__()
        self.command_functions = {
            'acquire': self.acquire_spectrum,
            'calibrate': self.calibrate_spectrometer
        }

        self._integrity_checker()

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown spectrometer command: '{command}'")
        return self.command_functions[command](*args, **kwargs)

    @ui_callable
    def acquire_spectrum(self):
        print("Acquiring a spectrum from the spectrometer.")

    @ui_callable
    def calibrate_spectrometer(self):
        print("Calibrating the spectrometer.")

class StageControl(Instrument):
    def __init__(self):
        super().__init__()
        self.command_functions = {
            'move': self.move_stage,
            'home': self.home_stage
        }

        self._integrity_checker()

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown stage command: '{command}'")
        return self.command_functions[command](*args, **kwargs)

    @ui_callable
    def move_stage(self):
        print("Moving the stage.")

    @ui_callable
    def home_stage(self):
        print("Homing the stage.")


class Monochromator(Instrument):
    def __init__(self):
        super().__init__()
        self.command_functions = {
            'set_wavelength': self.set_wavelength,
            'get_wavelength': self.get_wavelength
        }

        self._integrity_checker()

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown monochromator command: '{command}'")
        return self.command_functions[command](*args, **kwargs)

    @ui_callable
    def set_wavelength(self):
        print("Setting the monochromator wavelength.")

    @ui_callable
    def get_wavelength(self):
        print("Getting the monochromator wavelength.")