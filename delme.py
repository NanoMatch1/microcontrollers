import json
import os
import numpy as np
from types import SimpleNamespace

jsonfile = os.path.join(os.path.dirname(__file__), 'calibrations.json')

load_json = lambda: json.load(open(jsonfile, 'r'))

# print(load_json())


test = SimpleNamespace(**{calib: np.poly1d(calib) for calib in load_json()})

print(test)

breakpoint()

print('st')