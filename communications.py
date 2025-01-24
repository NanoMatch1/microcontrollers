import os
import time
from commands import CommandHandler

class CommunicationHandler:
    def __init__(self):
        # Example dictionaries from your original code:
        self.general_dict = {}
        self.apd_dict = {}
        self.tuning_motor_dict = {}
        self.laser_dict = {}
        self.microscope_functions = {}
        self.camera_dict = {}
        self.spectrometer_dict = {}
        self.stage_dict = {}
        
        # Setup a command-handler map
        self.command_handlers = {
            'eept': self.handle_eept,
            'aapt': self.handle_aapt
        }

        # Because you have separate dictionaries for certain command sets (general, apd, tuning_motor, etc.),
        # you can also handle them collectively in a second lookup step if you want:
        # Or you can put them in self.command_handlers one by one. Both approaches work.

        self.report = False
        self.scriptDir = "/some/default/path"
        # self.uno_serial, self.laser_serial, self.camera, etc. are assumed set up.

    def process_coms(self, coms: str):
        """
        Main dispatcher: breaks the input string into tokens,
        then routes the command to the correct handler function.
        """
        tokens = [item.lower() for item in coms.split(' ')]
        if not tokens:
            print("No command given.")
            return

        # cmd = tokens[0]

        command = CommandHandler(tokens)

        # 1) Check if this is a top-level command handled by our command_handlers dict:
        if cmd in self.command_handlers:
            return self.command_handlers[cmd](tokens)

        # 2) Check if it's in the general_dict or other specialized dict:
        elif cmd in self.general_dict:
            return self.handle_general(tokens)

        elif cmd in self.apd_dict:
            return self.handle_apd(tokens)

        elif cmd in self.tuning_motor_dict:
            return self.handle_tuning_motor(tokens)

        elif cmd in self.laser_dict:
            return self.handle_laser(tokens)

        elif cmd in self.microscope_functions:
            return self.handle_microscope(tokens)

        elif cmd in self.camera_dict:
            return self.handle_camera(tokens)

        elif cmd in self.spectrometer_dict:
            return self.handle_spectrometer(tokens)

        elif cmd in self.stage_dict:
            return self.handle_stage(tokens)

        else:
            print(f"Command not recognized: {cmd}")
            return None

    # ----------------------
    # COMMAND HANDLER EXAMPLES
    # ----------------------

    def handle_eept(self, tokens):
        """
        Original code for the 'eept' command is pulled out here.
        """
        # tokens[0] = 'eept', tokens[1:] could be extras
        # Use a helper function to parse the "extra" argument
        extra = self.parse_extra(tokens[1:])

        # Perform the repeated steps in sub-methods or inline
        gpa = self.get_position('gpa')
        gpb = self.get_position('gpb')

        with open(os.path.join(self.scriptDir, 'eept.txt'), 'a') as f:
            f.write(f"{gpa}:{gpb}:{extra}\n")
        print(f'exporting {gpa}:{gpb}:{extra}')
        return f'exporting {gpa}:{gpb}'

    def handle_aapt(self, tokens):
        """
        Original code for the 'aapt' command.
        """
        extra = self.parse_extra(tokens[1:])

        gpa = self.get_position('gpa', read_index=0)
        gpb = self.get_position('gpb', read_index=0)

        laser_wavelength, _ = self.calculate_laser_wavelength()
        grating_wavelength = self.grating_wavelength[0]

        with open(os.path.join(self.scriptDir, 'aapt.txt'), 'a') as f:
            f.write(f"{laser_wavelength}:{gpa}:{gpb}:{grating_wavelength}\n")
        print(f'exporting {laser_wavelength}:{gpa}:{gpb}:{grating_wavelength}')
        return f'exporting {laser_wavelength}:{gpa}:{gpb}:{grating_wavelength}'

    def handle_general(self, tokens):
        """
        For commands in self.general_dict
        """
        # tokens[0] in self.general_dict
        self.general_dict[tokens[0]]()
        return f'Connected to {tokens[0]}'

    def handle_apd(self, tokens):
        """
        For commands in self.apd_dict
        """
        cmd = tokens[0]
        if len(tokens) > 1:
            command = f"m{self.apd_dict[cmd]}{tokens[1]}m"
        else:
            command = f"m{self.apd_dict[cmd]}m"
        print(f"UI>UNO:{command}")
        self.send_command_to_UNO(command)
        time.sleep(0.1)
        response = self.read_from_serial_until()
        return response

    def handle_tuning_motor(self, tokens):
        """
        For commands in self.tuning_motor_dict
        """
        cmd = tokens[0]
        if len(tokens) > 1:
            command = f"o{self.tuning_motor_dict[cmd]}{tokens[1]}o"
        else:
            command = f"o{self.tuning_motor_dict[cmd]}o"
        print(f"UI>UNO:{command}")
        self.send_command_to_UNO(command)
        time.sleep(0.1)
        return self.read_from_serial_until()

    def handle_laser(self, tokens):
        """
        For commands in self.laser_dict
        """
        cmd = tokens[0]
        command = self.laser_dict[cmd]
        self.send_command_to_laser(command)
        time.sleep(0.01)
        response = self.read_from_laser()
        print(response)
        return response

    def handle_microscope(self, tokens):
        """
        For commands in self.microscope_functions
        """
        cmd = tokens[0]
        if len(tokens) > 1:
            return self.microscope_functions[cmd](*tokens[1:])
        else:
            return self.microscope_functions[cmd]()

    def handle_camera(self, tokens):
        """
        For commands in self.camera_dict
        """
        cmd = tokens[0]
        reset = False
        if self.camera.is_running:
            reset = True
            self.stop_continuous_acquire()

        if len(tokens) > 1:
            self.camera_dict[cmd](*tokens[1:])
        else:
            self.camera_dict[cmd]()

        if reset:
            self.continuous_acquire()

        return None

    def handle_spectrometer(self, tokens):
        """
        For commands in self.spectrometer_dict
        """
        cmd = tokens[0]
        if len(tokens) > 1:
            command = f"{self.spectrometer_dict[cmd]} {tokens[1]}"
        else:
            command = self.spectrometer_dict[cmd]
        response = self.send_command_to_spectrometer(command)
        return response

    def handle_stage(self, tokens):
        """
        Placeholder for stage control
        """
        return None

    # ---------------------------------
    # HELPER/UTILITY METHODS
    # ---------------------------------

    def parse_extra(self, tokens):
        return ",".join(tokens) if tokens else ""

    def get_position(self, motor_key, read_index=1):
        """
        Example helper that consolidates reading position from motors.
        read_index can be 0 or 1 depending on your original code structure.
        """
        command = f"o{self.tuning_motor_dict[motor_key]}o"
        self.send_command_to_UNO(command)
        time.sleep(0.1)
        response = self.read_from_serial_until()
        # Safeguard in case response is empty or short
        if not response or len(response) <= read_index:
            return None
        # Example parse logic:
        raw_val = response[read_index].split('<P')[1]
        raw_val = raw_val.split('P>')[0]
        return raw_val.split(',')

    def send_command_to_UNO(self, command):
        self.uno_serial.write((command + '\n').encode())
        time.sleep(0.1)

    def read_from_serial_until(self, end_flag='#CF'):
        end_responses = []
        while True:
            response = self.read_command_from_uno()
            if response == '':
                time.sleep(0.01)
                continue
            if self.report:
                print(response)
            split_responses = response.split('\r\n')
            for item in split_responses:
                if item == end_flag:
                    return end_responses
                if item != '':
                    end_responses.append(item)
            time.sleep(0.01)

    def read_command_from_uno(self):
        # Implementation depends on how you read lines from self.uno_serial
        # e.g. return self.uno_serial.readline().decode().strip()
        return ""

    def send_command_to_laser(self, command):
        pass

    def read_from_laser(self):
        pass

    def calculate_laser_wavelength(self):
        return (532, 650)  # example

    def stop_continuous_acquire(self):
        pass

    def continuous_acquire(self):
        pass

    def send_command_to_spectrometer(self, command):
        pass
