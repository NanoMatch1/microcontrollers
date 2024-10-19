# Import the .NET class library
import clr

# Import python sys module
import sys

# Import os module
import os

# Import System.IO for saving and opening files
from System.IO import *
from System.Threading import AutoResetEvent

# Import C compatible List and String
from System import String
from System.Collections.Generic import List

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import DeviceType
from PrincetonInstruments.LightField.AddIns import ExperimentSettings




def set_value(setting, value):    
    # Check for existence before setting
    # gain, adc rate, or adc quality
    if experiment.Exists(setting):
        experiment.SetValue(setting, value)

def device_found():
    # Find connected device
    for device in experiment.ExperimentDevices:
        if (device.Type == DeviceType.Camera):
            return True
     
    # If connected device is not a camera inform the user
    print("Camera not found. Please add a camera and try again.")
    return False  

def experiment_completed(sender, event_args):
    print("...Acquisition Completed")
    acquireCompleted.Set()


        
# Create the LightField Application (true for visible)
# The 2nd parameter forces LF to load with no experiment 
auto = Automation(True, List[String]())

# Get experiment object
experiment = auto.LightFieldApplication.Experiment
acquireCompleted = AutoResetEvent(False)
experiment.Load("Automation")
experiment.ExperimentCompleted += experiment_completed



if (device_found()==True): 
    #Set exposure time
    set_value(CameraSettings.ShutterTimingExposureTime, 20.0)

    # Acquire image
    # experiment.Acquire()

while True:
    acq_time = input("enter acq time")
    try:
        acq_time = float(acq_time)
        set_value(CameraSettings.ShutterTimingExposureTime, acq_time*1000)
    except ValueError:
        print("enger a valid number")
    
    filename = input("enter a filename")
    experiment.SetValue(ExperimentSettings.FileNameGenerationBaseFileName, filename)

    experiment.Acquire()



    

breakpoint()
print('end')