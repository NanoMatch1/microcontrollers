import json
import shutil
import os

scritDir = os.path.dirname(__file__)
file_type = 'pixel_cal'

for file in os.listdir(scritDir):
    if file.endswith('.json'):
        file_path = os.path.join(scritDir, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            data['data_type'] = file_type
            # breakpoint()
        
        new_file_path = os.path.join(scritDir, file)
        with open(new_file_path, 'w') as f:
            json.dump(data, f)
        
    
    