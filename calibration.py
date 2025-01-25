import os
import numpy as np
import json
from types import SimpleNamespace

class PolySinModulation:
    def __init__(self, a2, a1, a0, A, B, C, D):
        """
        Initialize the polynomial and sinusoidal coefficients.
        Polynomial: a2*x^2 + a1*x + a0
        Sinusoidal modulation: A*sin(B*x + C) + D
        """
        self.a2 = a2
        self.a1 = a1
        self.a0 = a0
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def __call__(self, x):
        """
        Evaluate the polynomial + sinusoidal modulation at the given x value.
        """
        poly = self.a2 * x**2 + self.a1 * x + self.a0
        modulation = self.A * np.sin(self.B * x + self.C) + self.D
        return poly + modulation

    def __repr__(self):
        """
        String representation of the polynomial and sinusoidal components.
        """
        poly_part = f"{self.a2}*x^2 + {self.a1}*x + {self.a0}"
        sin_part = f"{self.A}*sin({self.B}*x + {self.C}) + {self.D}"
        return f"PolySinModulation: ({poly_part}) + ({sin_part})"

class LinSinModulation:
    '''Class for linear + sinusoidal modulation fit.'''
    def __init__(self, a1, a0, A, B, C, D):
        self.a1 = a1
        self.a0 = a0
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def __call__(self, x):
        linear = self.a1 * x + self.a0
        modulation = self.A * np.sin(self.B * x + self.C) + self.D
        return linear + modulation
    
    def __repr__(self):
        linear_part = f"{self.a1}*x + {self.a0}"
        sin_part = f"{self.A}*sin({self.B}*x + {self.C}) + {self.D}"
        return f"LinSinModulation: ({linear_part}) + ({sin_part})"
    
class Calibration:

    def __init__(self, interface):
        self.scriptDir = interface.scriptDir
        self.calibrationDir = os.path.join(self.scriptDir, 'calibrations')
        self._generate_calibrations()
    
    def _load_calibrations(self):
        """
        Load the calibration data from the calibrations_main.json file.
        """
        with open(os.path.join(self.scriptDir, 'calibrations', 'calibrations_main.json'), 'r') as f:
            calibrations = json.load(f)
            print('Calibrations loaded from file')
        return calibrations

    def _generate_calibrations(self, report=False):
        self.all_calibrations = self._load_calibrations()
        # self.calibrations = SimpleNamespace()
        
        for name, calib in self.all_calibrations.items():
            if len(calib) == 7:
                print("Loading {} as poly_sin".format(name))
                self.__setattr__(name, PolySinModulation(*calib))
            if len(calib) == 6:
                print("Loading {} as poly_sin".format(name))
                self.__setattr__(name, LinSinModulation(*calib))
            else:
                print("Loading {} as poly1d".format(name))
                self.__setattr__(name, np.poly1d(calib))

        self.g1_to_wl = self.g1_to_wl_subtractive
        self.wl_to_g1 = self.wl_to_g1_subtractive

        print("Calibrations successfully built.")



class ldrScans:

    def __init__(self):
        self.l2 = {
            'range': 150,
            'resolution': 5,
        }
        self.g1 = {
            'range': 150,
            'resolution': 5,
        }
        self.g2 = {
            'range': 150,
            'resolution': 5,
        }