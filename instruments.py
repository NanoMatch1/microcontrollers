import inspect
import serial
import time
import pyvisa

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps

from calibration import Calibration

def simulate(expected_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.simulate:
                return expected_value
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def ui_callable(func):
    """
    Decorator that marks a method as UI-callable by
    setting a custom attribute on the function object.
    """
    func.is_ui_process_callable = True
    return func

@dataclass
class MotorPositions:
    x: int
    y: int
    z: int
    a: int

class AcquitisionParameters:
    '''Holds the acquisition parameters for the microscope, and is passed to acquisition methods to perform actions.'''
    def __init__(self):
        self.scan_min = None
        self.scan_max = None
        self.scan_resolution = None
        self.acq_time = None

    @ui_callable
    def set_scan_min(self, value):
        try:
            self.scan_min = int(value)
        except ValueError:
            print('Invalid value for scan min')
        print('Scan Min: {}'.format(self.scan_min))

    @ui_callable
    def set_scan_max(self, value):
        try:
            self.scan_max = int(value)
        except ValueError:
            print('Invalid value for scan max')
        print('Scan Max: {}'.format(self.scan_max))
    
    @ui_callable
    def set_scan_resolution(self, value):
        try:
            self.scan_resolution = int(value)
        except ValueError:
            print('Invalid value for scan resolution')
        print('Scan Resolution: {}'.format(self.scan_resolution))

    @ui_callable
    def set_acquisition_time(self, acq_time):
        try:
            self.acq_time = float(acq_time)
        except ValueError:
            print('Invalid value for acquisition time')
        print('Acquisition Time Set: {}'.format(self.acq_time))

class MotionControl:
    '''Handles the motion control of the microscope. Needs access to the controller to move the motors.'''
    def __init__(self, controller):
        self.controller = controller
        self._grating_steps = None
        self._laser_steps = None
        self._spectrometer_position = None

        self._laser_wavelength = None
        self._grating_wavelength = None
        self._spectrometer_wavelength = None

        self.hard_limits = {
            'laser_wavelength': [650, 1000],
            'grating_wavelength': [500, 1300],
        }

    def close_mono_shutter(self):
        self.controller.send_command('gsh on')

    def open_mono_shutter(self):
        self.controller.send_command('gsh off')

    @ui_callable
    def get_laser_motor_positions(self, *args):
        '''Get the current positions of the laser motors.'''
        self.laser_steps = self.controller.get_laser_motor_positions()
        print('Current laser pos: {}'.format(self.laser_steps))

        return self.laser_steps
    
    @ui_callable
    def get_grating_motor_positions(self, *args):
        '''Get the current positions of the grating motors.'''
        self.grating_steps = self.controller.get_grating_motor_positions()
        print('Current grating pos: {}'.format(self.grating_steps))

        return self.grating_steps

    @property
    def laser_wavelength(self):
        return self._laser_wavelength

    @laser_wavelength.setter
    def laser_wavelength(self, value): 
        self._laser_wavelength = value

    @property
    def grating_steps(self):
        return self._grating_steps
    
    @grating_steps.setter
    def grating_steps(self, value):
        if len(value) != 4 or not all(isinstance(x, int) for x in value):
            print('Invalid grating steps')
        self._grating_steps = value

    @property
    def laser_steps(self):
        return self._laser_steps
    
    @laser_steps.setter
    def laser_steps(self, value):
        if len(value) != 4 or not all(isinstance(x, int) for x in value):
            print('Invalid laser steps')
        self._laser_steps = value

    def check_hard_limits(self, value, limits):
        '''Checks the hard limits dictionary of the microscope for the allowed range of values.'''
        if not limits[0] < value < limits[1]:
            return False
        
    def check_laser_wavelength(self, wavelength):
        '''Checks the validity of the entered value for laser wavelength.'''
        try:
            wavelength = float(wavelength)
        except ValueError:
            print('Invalid value for wavelength - use a number')
            return False
        
        if not self.check_hard_limits(wavelength, self.hard_limits['laser_wavelength']):
            print('Wavelength out of range. Pick a wavelength between {} and {} nm'.format(*self.hard_limits['laser_wavelength']))
            return False
        
        return True
        

    def go_to_laser_wavelength(self, wavelength, autoshutter=True):

        if self.check_laser_wavelength(wavelength) is False:
            return False
        
        self.close_mono_shutter()

        current_pos = self.get_laser_motor_positions()
        if current_pos is None:
            return 

        l1_target = round(self.calibrations.wl_to_l1(wavelength))
        # print("l1 target: {}".format(l1_target))

        l2_target = round(self.calibrations.wl_to_l2(wavelength))
        # print("l2 target: {}".format(l2_target))
        print('Current laser position: {}'.format(current_pos))
        print('Target laser position: {}'.format([l1_target, l2_target]))
        if l1_target == current_pos[0] and l2_target == current_pos[1]:
            print('Laser already at target position')
            return
        move_l1 = l1_target - current_pos[0]
        move_l2 = l2_target - current_pos[1]
        print("moving l1 by {}".format(move_l1))

        backlash = False
        # self.move_to(target_pos)
        if move_l1 != 0:
            if move_l1 < 0:
                backlash = True
            response = self.process_coms('l1 {}'.format(move_l1))

        if move_l2 != 0:
            if move_l2 < 0:
                backlash = True
            response = self.process_coms('l2 {}'.format(move_l2))

        # self.wait_for_motors_manual([l1_target, l2_target, 0, 0], 'A')
        self.wait_for_motors()

        if backlash:
            response = self.process_coms('l1 -20')
            response = self.process_coms('l2 -20')
            time.sleep(0.1)
            response = self.process_coms('l1 20')
            response = self.process_coms('l2 20')

        self.confirm_motor_positions([l1_target, l2_target, 0, 0], 'A')
        self.laser_steps[0] = l1_target
        self.laser_steps[1] = l2_target

        print('Laser excitation at {}'.format(wavelength))
        # if autoshutter is True:
        self.laser_safety_check()
            # self.open_pinhole_shutter() # add check that light levels are safe #TODO: Add this check
        self.open_mono_shutter()

        self.calculate_laser_wavelength(self.laser_steps)


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

    def __init__(self, interface, simulate=False):
        super().__init__()
        self.interface = interface
        self.controller = interface.controller
        self.simulate = simulate

        self.command_functions = {
            'wai': self.where_am_i,
            'rg': self._get_spectrometer_position,
            'apos': self.get_laser_motor_positions,
            'bpos': self.get_grating_motor_positions,
            'scanmin': self.acquisition_parameters.set_scan_min,
            'scanmax': self.acquisition_parameters.set_scan_max,
            'scanres': self.acquisition_parameters.set_scan_resolution,
            'acqtime': self.acquisition_parameters.set_acquisition_time,
        }

        # scientific attributes
        self.laser_steps = None
        self.laser_wavelength = None
        self.grating_steps = None
        self.grating_wavelength = None
        self.spectrometer_position = None
        self.current_shift = 0

        # acquisition parameters
        self.acquisition_parameters = AcquitisionParameters()

        self.calibrations = self._generate_calibrations()
        self.calibrations.ammend_calibrations()
        self.calibrations.fix_subtractive_calibrations() # TODO: remove after recalibration subtractive
        self._integrity_checker()  # Validate on init

    def __str__(self):
        return "Microscope"

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown command: '{command}'")
        return self.command_functions[command](*args, **kwargs)
       
    
    def _generate_calibrations(self):
        return Calibration(self)
    
    @ui_callable
    def where_am_i(self):
        self.get_all_current_positions()
        self.report_all_current_positions()

    @ui_callable
    def _get_spectrometer_position(self):
        '''Get the current position of the spectrometer in motor steps.'''
        self.spectrometer_position = self.interface.spectrometer.get_spectrometer_position()
        print('Current spectrometer position: {}'.format(self.spectrometer_position))
        return self.spectrometer_position
    

    
    def get_all_current_positions(self):
        '''Get the current positions of all motors and calculate the corresponding wavelengths.'''
        laser_positions = self.calculate_laser_wavelength()
        grating_positions = self.calculate_grating_wavelength()
        spectrometer_position = self.calculate_spectrometer_wavelength()

        return (laser_positions, grating_positions, spectrometer_position)
    
    def calculate_spectrometer_wavelength(self, steps=None):
        '''Uses calibration to calculate wavelength from reported position. For spectrometers that report wavelength, this is a pass-through.'''
        if steps is None:
            steps = self.interface.spectrometer.get_spectrometer_position()
            self.spectrometer_position = steps

        self.spectrometer_wavelength = self.calibrations.triax_steps_to_wl(self.spectrometer_position) # TODO: rename triax_steps_to_wl to spectrometer_steps_to_wl - requires change to calibration files and will be breaking until otherwise completed
        return self.spectrometer_wavelength
    
    def report_all_current_positions(self):
        '''Formats and prints the current positions of the microscope.'''

        l1_wavelength, l2_wavelength, _, _ = [round(x, 2) for x in self.laser_wavelength]
        g1_wavelength, g2_wavelength, _, _ = [round(x, 2) for x in self.grating_wavelength]
        spectrometer_wavelength = round(self.spectrometer_wavelength, 2)

        print('laser pos: {}'.format(self.laser_steps))
        print('grating pos: {}'.format(self.grating_steps))
        print('triax pos: {}'.format(self.spectrometer_position))

        print('triax wavelength: {}'.format(spectrometer_wavelength))
        print('l1 wavelength: {}'.format(l1_wavelength))
        print('l2 wavelength: {}'.format(l2_wavelength))
        print('g1 wavelength: {}'.format(g1_wavelength))
        print('g2 wavelength: {}'.format(g2_wavelength))
        print('Raman shift: {}'.format(self.current_shift))

        return 
    
    def calculate_laser_wavelength(self, current_pos=None):
        if current_pos is None:
            current_laser_pos = self.controller.get_laser_motor_positions()
        else:
            current_laser_pos = current_pos

        self.laser_steps = current_laser_pos

        l1_pos = current_laser_pos[0]
        l2_pos = current_laser_pos[1]

        l1_wavelength = self.calibrations.l1_to_wl(l1_pos)
        l2_wavelength = self.calibrations.l2_to_wl(l2_pos)

        self.laser_wavelength = [l1_wavelength, l2_wavelength, 0, 0]
        
        # print('Current laser wavelength: {}'.format(l1_wavelength))
        return (l1_wavelength, l2_wavelength, 0, 0)
    

    
    def calculate_grating_wavelength(self, steps=None):
        if steps is None:
            current_grating_pos = self.controller.get_grating_motor_positions()
        else:
            current_grating_pos = steps

        g1_pos = current_grating_pos[0]
        g2_pos = current_grating_pos[1]

        self.grating_steps = current_grating_pos

        g1_wavelength = self.calibrations.g1_to_wl(g1_pos)
        g2_wavelength = self.calibrations.g2_to_wl(g2_pos)

        self.grating_wavelength = [g1_wavelength, g2_wavelength, 0, 0]

        return (g1_wavelength, g2_wavelength, 0, 0)

    def go_to_wavenumber(self, wavenumber):
        try:
            wavenumber = float(wavenumber)
        except ValueError:
            print('Invalid value for wavenumber - use a number')
            return
        if self.laser_wavelength is None:
            self.get_all_current_positions()
        
        # ;
        laser_wavenumber = self.current_laser_wavenumber
        # 
        wave = laser_wavenumber - wavenumber
        new_wavelength = 10_000_000/wave
        self.go_to_grating_wavelength(new_wavelength)
        self.current_shift = wavenumber
        
        print('Moving to wavenumber: {} for {} nm excitation'.format(wavenumber, self.laser_wavelength[0]))

class Camera(Instrument):
    def __init__(self, interface, simulate=False):
        super().__init__()
        self.interface = interface
        self.simulate = simulate
        self.command_functions = {
            'capture': self.capture_frame
        }

        self._integrity_checker()

    def __str__(self):
        return "Camera"

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown camera command: '{command}'")
        return self.command_functions[command](*args, **kwargs)
    
    def connect(self):
        print("Connecting to the camera.")
        self.serial = self.connect_to_camera()

    @simulate(expected_value=serial.Serial)
    def connect_to_camera(self):
        return serial.Serial

    @ui_callable
    def capture_frame(self):
        '''Record a frame from the camera.'''
        print("Capturing a frame from the camera.")

class Spectrometer(Instrument):
    def __init__(self, interface, simulate=False):
        super().__init__()
        self.interface = interface
        self.simulate = simulate
        self.command_functions = {
            'get_spectrometer_position': self.get_spectrometer_position,
            'go_to_position': self.go_to_position
        }

        self._integrity_checker()

    def __str__(self):
        return "Spectrometer"

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown spectrometer command: '{command}'")
        return self.command_functions[command](*args, **kwargs)

    @abstractmethod
    @ui_callable
    def get_spectrometer_position(self):
        print("Getting the current position of the spectrometer.")

    @abstractmethod
    @ui_callable
    def go_to_position(self, position):
        print("Going to the position: {}".format(position))



class Triax(Spectrometer):
    def __init__(self, interface, simulate=False):
        super().__init__(interface, simulate)

        self.command_functions = {
            'get_spectrometer_position': self.get_spectrometer_position,
            'rg': self.get_spectrometer_position,
            'go_to_position': self.go_to_position
        }


        self.message_map = {
            'initialise': 'A',
            'comsmode': '02000',
            'get_grating_steps': 'H0',
            'read_grating': 'H0',
            'rg': 'H0',
            'grating': 'F0,',
            'move_grating': 'F0,',
            'mg': 'F0,',
            'read_enter': 'j0,0',
            'ren': 'j0,0',
            'read_exit': 'j0,3',
            'rex': 'j0,3',
            'move_enter': 'k0,0,',
            'men': 'k0,0,',
            'move_exit': 'k0,3,',
            'mex': 'k0,3,',
            'tpol': 'E', # poll motors after move command sent
            'ccd_mode': 'f0',
            'ccd': 'f0',
            'apd_mode': 'e0',
            'apd': 'e0',
            # 'gotoir': 'F0,375131'
            #'entrance mirror to front enterance': 'c0',
            #'entrance mirror to side enterance': 'd0'
        }

        self._integrity_checker()

    def __str__(self):
        return "TRIAX Spectrometer"

    @ui_callable
    @simulate(expected_value=380000) # TODO: Change to actual response
    def get_spectrometer_position(self):
        '''Get the current position of the spectrometer in motor steps.'''
        print("Getting the current position of the TRIAX spectrometer.")
        current_position = self._get_triax_steps()
        return current_position
    
    @ui_callable
    @simulate(expected_value='OK') # TODO: Change to actual response
    def go_to_position(self, position):
        print("Going to the position: {}".format(position))
        command = self.message_map['move_grating'] + str(position)
        response = self._send_command_to_spectrometer(command)
        return response

    @simulate(expected_value=True) # TODO: Change to actual response
    def connect(self):
        # Open a connection to the instrument
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        self.spectrometer = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument

        self.spectrometer.write('WHERE AM I')
        time.sleep(0.0001)
        self.state = self.spectrometer.read()
        print(self.state)

        print('Connected to TRIAX spectrometer.')

        return self.spectrometer, self.state

    def _get_triax_steps(self):
        '''Polls the spectrometer for position and returns the current position in steps.'''
        response = self._send_command_to_spectrometer(self.message_map['get_grating_steps'])
        self.triax_steps = int(response.strip()[1:])
        return self.triax_steps
    
    def send_command(self, command):
        '''Send a command to the spectrometer.'''
        coms = self.message_map.get(command, None)
        if coms is None:
            print('Invalid command: {}'.format(command))
            return
        
        response = self._send_command_to_spectrometer(coms)
        return response
    
    def _send_command_to_spectrometer(self, command, report=True):
        self.spectrometer.write(command)
        time.sleep(0.0001)

        if command == 'A':
            count = 100
            while count > 0:
                print('Initialising: Sleeping for {} seconds'.format(count))
                time.sleep(1)
                count -= 1
        
        response = self.spectrometer.read()
        return response

class StageControl(Instrument):
    def __init__(self, interface, simulate=False):
        super().__init__()
        self.interface = interface
        self.simulate = simulate
        self.command_functions = {
            'move': self.move_stage,
            'home': self.home_stage
        }

        self._integrity_checker()

    def __str__(self):
        return "Stage Control"

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
    def __init__(self, interface, simulate=False):
        super().__init__()
        self.interface = interface
        self.simulate = simulate
        self.command_functions = {
            'set_wavelength': self.set_wavelength,
            'get_wavelength': self.get_wavelength
        }

        self._integrity_checker()

    def __str__(self):
        return "Monochromator"

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown monochromator command: '{command}'")
        return self.command_functions[command](*args, **kwargs)

    @ui_callable
    def set_wavelength(self):
        print("Setting the monochromator wavelength.")

    def go_to_grating_wavelength(self, wavelength):
        print(f"Going to grating wavelength: {wavelength}")


    @ui_callable
    def get_wavelength(self):
        print("Getting the monochromator wavelength.")

class Laser(Instrument):
    def __init__(self, interface, simulate=False):
        super().__init__()
        self.interface = interface
        self.simulate = simulate
        self.command_functions = {
            'set_power': self.set_power,
            'get_power': self.get_power
        }

        self._integrity_checker()

    def __str__(self):
        return "Laser"

    def __call__(self, command: str, *args, **kwargs):
        if command not in self.command_functions:
            raise ValueError(f"Unknown laser command: '{command}'")
        return self.command_functions[command](*args, **kwargs)
    
    def connect(self):
        print("Connecting to the laser.")
        pass

    @ui_callable
    def set_power(self):
        '''Set the laser power.'''
        print("Setting the laser power.")

    @ui_callable
    def get_power(self):
        '''Get the laser power.'''
        print("Getting the laser power.")