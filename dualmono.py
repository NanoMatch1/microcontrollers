class DualMonochromator:

    def __init__(self, microscope):
        self.microscope = microscope
        self.get_motor_positions()

        self.current_mode = 'additive'
        self.current_pos = (0, 0)

    def get_motor_positions(self):
        response = self.microscope.process_coms('Cgetinfo')
        if response == 'NONE':
            initial_pos = self.current_pos()
            home_pos = self.home_motors()

    
    def home_motors(self):
        response = self.microscope.process_coms('Chome')
        self.current_pos = (0, 0)
        return response
    
    def calibration_1(self, wavelength):
        return # function from calibration file, creating a position in steps for motor 1
    
    def calibration_2(self, wavelength):
        return # function from calibration file, creating a position in steps for motor 2
    
    def move_to(self, target_pos):
        motor_1_pos = self.calibration_1(target_pos)
        motor_2_pos = self.calibration_2(target_pos)

        response = self.microscope.process_coms('Cmove {} {}'.format(motor_1_pos, motor_2_pos))
        if response == 'OK':
            self.current_pos = (motor_1_pos, motor_2_pos)
        else:
            print('Error moving monochromator motors')
            print(response)
        pass

    def load_calibrations(self):
        if self.current_mode == 'additive':
            # load additive calibration file
            # self.load_additive_calibration()
            # Shoudl contain calibration for motor 1 and motor 2
            pass
        elif self.current_mode == 'subtractive':
            # load subtractive calibration file
            pass
            # self.load_subtractive_calibration()
            # Should contain calibration for motor 1 and motor 2
    

        


    def add_mode(self):
        pass