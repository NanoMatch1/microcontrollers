

'''Code plan.
Make dual monochromator class. The mono should know what mode it is in based on a current or previous format. 
The class is a wrapper for communication with an individual microcontroller. 
1. It should, on initialisation, send a message to the microcontroller and request motor positions and current mode.
    a. the current mode should be conveyed to the microcontroller and stored there
2. if the microcontroller does not have the required information (such as during boot), the mono should home itself.
    a. before homing, it should save the current position, so that it can return here, including backlash compensation.
3. all motors should operate under a backlash compensation regime, and approach the target position from the same direction.
4. the mono should have a method for moving to a target position, and a method for moving to a target wavelength. 
    a. in Additive mode, Target wavelength will be the primary method for moving the mono.
    b. in subtractive mode, the target wavelength will also be the primary method for moving, but in this case the target wavelength needs to be BLOCKED rather than transmitted.
        i. therefore, a two calibration files need to be stored, one for each mode. In additive, the calibration tells the code what wavelength transmission correspons to what motor position. In subtractive, the calibration tells the code what motor position causes the desired wavelength to be blocked.
        ii. there should be a correction factor which allows one to get closer to the laser line. The correction factor applied will be in units of wavenumbers, which are calibrated to steps by the calibration file.
5. for safety, the mono class should only allow movement of the motors when the beam is blocked. This can be achieved by having a method which checks the beam status within the microscope class, and if the beam is not blocked, it will block the beam and then move the motors.

there will be homing motors that the monochromator should.'''


# class Calibrations:

#     def __init__(self, calibrations):
#         self.coefficients = calibrations
#         # self.__dict__.update(np.poly1d(calibrations))
#         self.__dict__.update({calib: np.poly1d(self.coefficients[calib]) for calib in self.coefficients})
        
'''Items still to do:
Phase 1: High priority
    1. Add shutter for safety. Use single power mosfet to feed 3-5V power to the shutter.
        a. Edit the pinhole shutter method to drive this shutter.
    2. Bring PICAM interface into the microscope. Use a separate class and feed it to the microscope class/microscope class to it.
    2. Create methods for:
        a. Acquiring a spectrum of a given range. This requires multiple scans and stitching them together. Note this can now be done internally using the PICAM interface
            i. write triax control code. needs polling method for moving motors
            i. This requires a data save method. use the ui to enter a filename, and save the data to a file.
        b. a basic laser excitation scan. This will simply acquire a spectrum at a range of wavelengths with a given resolution.
            i. make the scan method agnistic, so it can be used in the final version of the multidiemensional scans.
        c. Create a method for exporting a map of the data structure. This should eventually accommodate multi-dimensional data including wavelength, position, and polarization.

 >>> Start scanning MoS2 powder

Phase 2: In preparation of scanning MoS2 flakes
    1. Add motor control for the sample stage.
    2. Enclose system.
    3. Add input polarization control.
    4. Add output polarization control.
    5. Create multidimensional scan method.
    6. Motorise L3. Create calibration for L3.

>>> Scan MoS2 flakes or WSe2 flakes

Phase 3: Polishing the system
    1. Create homing protocols for all motors.
    2. Add control of laser
    3. Try changing spectrometer control to RS232/MEGA UART
    4. Create all autocalibration methods.
    5. Try switch to linux
    6. Build single board computer for control
'''