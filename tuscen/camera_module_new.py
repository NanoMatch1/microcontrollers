#!/usr/bin/env python
# coding: utf-8

import ctypes
from ctypes import byref
import os
import threading
import time
import numpy as np

import traceback

from ctypes import pointer
from TUCam import (
    TUCAM_INIT,
    TUCAM_OPEN,
    TUCAM_FRAME,
    TUCAM_ROI_ATTR,
    TUCAM_Buf_Alloc,
    TUCAM_Buf_Release,
    TUCAM_Buf_WaitForFrame,
    TUCAM_Buf_AbortWait,
    TUCAM_Cap_Start,
    TUCAM_Cap_Stop,
    TUCAM_Capa_SetValue,
    TUCAM_Prop_SetValue,
    TUCAM_Dev_Open,
    TUCAM_Dev_Close,
    TUCAM_Api_Init,
    TUCAM_Api_Uninit,
    TUCAM_CAPTURE_MODES,
    TUFRM_FORMATS,
    TUCAM_IDCAPA,
    TUCAM_IDPROP,
    TUCAM_Cap_SetROI,
    TUCAMRET,
    TUCAM_Prop_GetAttr,
    TUCAM_PROP_ATTR,
    TUCAM_CAPA_ATTR,
    TUCAM_Capa_GetAttr,
    TUCAM_Prop_GetValue,
)

# from TUCam import get_camera_gain_attributes    # If you have a local function to retrieve gain info

class TucamCamera:
    """
    A refactored camera class that encapsulates initialization,
    acquisition, and teardown for a Tucsen camera.
    """

    def __init__(self, interface=None, report=False):
        """
        Initialize the camera driver (but do not open a specific camera yet).
        """
        self.interface = interface
        self.report = report
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.transient_dir = self.interface.transientDir if self.interface else os.path.join(self.script_dir, 'transient')

        # acquisition parameters
        self.acqtime = 100 # milliseconds
        self.roi = (0, 0, 2048, 2048)
        self.roi = (0, 0, 1000, 1000)

        self.camera_parameters = {}
        self.camera_capabilities = {}


        # Thread-safety and acquisition flags
        self.camera_lock = threading.Lock()
        self.stop_flag = threading.Event()
        self.is_running = False

        self.command_functions = {
            "acquire": self.safe_acquisition,
            "run": self.start_continuous_acquisition,
            "stop": self.stop_continuous_acquisition,
            "refresh": self.refresh,
            "roi": self.set_roi,
            "acqtime": self.set_acqtime,
            "gain": self.set_gain,
            "gain_info": self.get_gain_attributes,
            "calibrate": self.calibrate_best_signal,
            "high_signal": self.set_high_signal_boost,
            "params": self.print_camera_params,
            "info": self.camera_info,
            "getinfo": self.get_camera_parameters,
            "debug": self.debug,
            "temp": self.check_camera_temperature,
            "longexp": self.set_long_exposure_mode,
            "fan": self.set_fan_speed,
            # "safe": self.safe_acquisition,

        }

        print('Print finished TucsenCamera init')

    def debug(self):
        print("Debugging...")
        breakpoint()

    def refresh(self):
        """
        Re-initialize the camera driver: closes and uninitializes the driver,
        then re-initializes. Useful if camera gets stuck or you want a clean reset.
        """
        print("Refreshing camera...")

        # Make sure to close if open, then uninit
        self.close_camera()
        self.uninit_api()

        # Re-init the TUCam API
        self.TUCAMINIT = TUCAM_INIT(0, self.script_dir.encode('utf-8'))
        TUCAM_Api_Init(pointer(self.TUCAMINIT), 5000)

        self.open_camera()

        self.set_acqtime(self.acqtime)
        self.set_roi(self.roi)
        print("Camera refresh complete.")


    # def open_camera(self, index=0):
    #     """
    #     Open a specific camera index after the API is initialized.
    #     """
    #     if index >= self.TUCAMINIT.uiCamCount:
    #         print(f"Camera index {index} not available!")
    #         return

    #     self.TUCAMOPEN = TUCAM_OPEN(index, 0)
    #     ret_code = TUCAM_Dev_Open(pointer(self.TUCAMOPEN))
    #     if self.TUCAMOPEN.hIdxTUCam == 0 or ret_code != 0:
    #         print("Open the camera failure!")
    #     else:
    #         print("Open the camera success!")
    def initialise(self):
        print("Initialising TUCam API...")
        # Prepare TUCAM structures
        self.TUCAMINIT = TUCAM_INIT(0, self.script_dir.encode('utf-8'))
        self.TUCAMOPEN = TUCAM_OPEN(0, 0)
        self.handle = self.TUCAMOPEN.hIdxTUCam

        # Initialize TUCam API
        TUCAM_Api_Init(pointer(self.TUCAMINIT), 5000)
        print("TUCam API initialized.")

        self.open_camera()
        self.set_acqtime(self.acqtime)
        self.set_roi(self.roi)




    def open_camera(self, Idx=0):

        if  Idx >= self.TUCAMINIT.uiCamCount:
            return

        print('Opening camera...')
        self.TUCAMOPEN = TUCAM_OPEN(Idx, 0)

        TUCAM_Dev_Open(pointer(self.TUCAMOPEN))

        if 0 == self.TUCAMOPEN.hIdxTUCam:
            print('Open the camera failure!')
            return
        else:
            print('Open the camera success!')

    def close_camera(self):
        """
        Close the currently open camera if any.
        """
        if self.TUCAMOPEN.hIdxTUCam != 0 and self.TUCAMOPEN.hIdxTUCam is not None:
            TUCAM_Dev_Close(self.TUCAMOPEN.hIdxTUCam)
            self.TUCAMOPEN.hIdxTUCam = 0  # Reset the handle
            print("Close the camera success")

    def uninit_api(self):
        """
        Uninitialize the TUCam API. Call this once you are done with all operations.
        """
        TUCAM_Api_Uninit()

    def safe_acquisition(self, target_temp=-5):
        """
        Acquires a frame, then waits for the temperature to drop before proceeding.
        """
        while True:
            temp = ctypes.c_double()
            TUCAM_Prop_GetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_TEMPERATURE.value, byref(temp), 0)

            if temp.value < target_temp:
                print(f"Temperature stable ({temp.value}°C). Acquiring frame...")
                return self.acquire_one_frame()
            else:
                print(f"Camera too hot ({temp.value}°C). Waiting...")
                time.sleep(5)  # Wait before checking temperature again

    def set_fan_speed(self, speed=3):
        """
        Adjusts the fan speed to enhance cooling.
        Speed Levels:
        0 - Off
        1 - Low
        2 - Medium
        3 - High (Recommended for cooling)
        """
        status = TUCAM_Capa_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDCAPA.TUIDC_FAN_GEAR.value, speed)

        if status == TUCAMRET.TUCAMRET_SUCCESS:
            print(f"Fan speed set to {speed} (High Recommended for Cooling).")
        else:
            print(f"Failed to set fan speed. Error code: {status}")


    def acquire_one_frame(self, export=True):
        """
        Acquire a single frame from the camera and return it as a numpy array.
        This function:
          1. Opens the camera (index=0 by default).
          2. Sets ROI, exposure, etc.
          3. Waits for exactly one frame.
          4. Closes the camera.
          5. Returns the frame data (numpy array).
        """
        # self.open_camera(0)
        # self.set_roi((0, 0, 2048, 2048))
        # self.set_acqtime(200)

        data_dict = self.wait_for_image_data(nframes=1)
        data = data_dict[0]
        # self.close_camera()
        if export is True:
            self.export_data(data, 'test', overwrite=False)
        if data_dict:
            return data_dict[0]
        else:
            return None

    def start_continuous_acquisition(self, roi=(0, 0, 2048, 2048), exposure=200):
        """
        Start a continuous acquisition thread until told to stop via stop_continuous_acquisition().
        Each frame is saved as .npy into self.transient_dir.
        """
        if self.is_running:
            print("Camera is already running continuous acquisition!")
            return

        # Set up for continuous acquisition
        def continuous_task():
            self.stop_flag.clear()
            # self.open_camera(0)
            # self.set_roi(roi)
            # self.set_acqtime(exposure)

            while not self.stop_flag.is_set():
                try:
                    with self.camera_lock:
                        data_dict = self.wait_for_image_data(nframes=1)
                    if not data_dict:
                        continue
                    data = data_dict[0]
                    self.export_data(data, 'transient_data', save_dir=self.transient_dir, overwrite=True)
                    time.sleep(0.001)
                    del data_dict
                except Exception as e:
                    print(f"Acquisition error: {e}")
                    print(traceback.format_exc())
                    break

            # self.close_camera()

        acq_thread = threading.Thread(target=continuous_task, daemon=True)
        acq_thread.start()

        self.is_running = True
        print("Started continuous acquisition.")

    def stop_continuous_acquisition(self):
        """
        Stop the continuous acquisition thread.
        """
        print("Stopping continuous acquisition.")
        self.stop_flag.set()
        self.is_running = False

    def wait_for_image_data(self, nframes=1):
        """
        Waits for camera frames and converts them to numpy arrays.
        Adjusts timeout dynamically based on exposure time.
        """
        data_dict = {}

        # Retrieve current exposure time
        exposure_time = ctypes.c_double()
        TUCAM_Prop_GetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_EXPOSURETM.value, byref(exposure_time), 0)

        # Ensure timeout is at least twice the exposure time (for safety margin)
        timeout = max(2 * exposure_time.value, 1000)  # Minimum 1000ms

        m_frame = TUCAM_FRAME()
        m_frame.pBuffer = 0
        m_frame.ucFormatGet = TUFRM_FORMATS.TUFRM_FMT_USUAl.value
        m_frame.uiRsdSize = 1

        # Allocate internal buffer
        TUCAM_Buf_Alloc(self.TUCAMOPEN.hIdxTUCam, pointer(m_frame))
        TUCAM_Cap_Start(self.TUCAMOPEN.hIdxTUCam, TUCAM_CAPTURE_MODES.TUCCM_SEQUENCE.value)

        for i in range(nframes):
            try:
                _ = TUCAM_Buf_WaitForFrame(self.TUCAMOPEN.hIdxTUCam, pointer(m_frame), int(timeout))
                print(f"Frame {i}: width={m_frame.usWidth}, height={m_frame.usHeight}")
            except Exception:
                print(f"Frame timeout exceeded ({timeout}ms). Increase timeout if necessary.")
                continue

            # Convert to numpy
            try:
                data = self._convert_to_numpy(m_frame)
                data_dict[i] = data
            except Exception as e:
                print(f"Convert to numpy failed for frame {i}: {e}")

        TUCAM_Buf_AbortWait(self.TUCAMOPEN.hIdxTUCam)
        TUCAM_Cap_Stop(self.TUCAMOPEN.hIdxTUCam)
        TUCAM_Buf_Release(self.TUCAMOPEN.hIdxTUCam)

        return data_dict
    
    def check_camera_temperature(self, report=True):
        """
        Checks and prints the current camera temperature.
        """
        temp = ctypes.c_double()
        status = TUCAM_Prop_GetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_TEMPERATURE.value, byref(temp), 0)

        if status == TUCAMRET.TUCAMRET_SUCCESS:
            if report:
                print(f"Camera Temperature: {round(temp.value, 2)}°C")
            if temp.value > 80:
                print("WARNING: Camera is overheating! Exposure time may be reduced automatically.")
        else:
            print(f"Failed to retrieve temperature. Error code: {status}")


    def set_long_exposure_mode(self):
        """
        Set the camera to a mode that best supports long exposures.
        """
        print("Setting camera to long exposure mode...")

        # 1. Set image mode to CMS (best for long exposure stability)
        status = TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDC_IMGMODESELECT.value, 1, 0)
        if status == TUCAMRET.TUCAMRET_SUCCESS:
            print("Set Image Mode to CMS (12-bit).")
        else:
            print("Failed to set Image Mode.")

        # 2. Disable automatic exposure control (if enabled)
        status = TUCAM_Capa_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDCAPA.TUIDC_ATEXPOSURE.value, 0)
        if status == TUCAMRET.TUCAMRET_SUCCESS:
            print("Disabled automatic exposure control.")
        else:
            print("Failed to disable automatic exposure control.")

        # 3. Ensure a stable gain setting (HighGain recommended)
        status = TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_GLOBALGAIN.value, 1, 0)
        if status == TUCAMRET.TUCAMRET_SUCCESS:
            print("Set Gain to HighGain.")
        else:
            print("Failed to set Gain.")


    def set_acqtime(self, value):
        """
        Set camera exposure time to 'value' (in microseconds or ms—depends on the camera).
        """
        try:
            value = float(value)
        except ValueError:
            print("Exposure time must be a number.")
            return
        
        TUCAM_Capa_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDCAPA.TUIDC_ATEXPOSURE.value, 0)
        TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_EXPOSURETM.value, value, 0)
        print(f"Set exposure to {value}")
    
    def print_camera_params(self):
        """
        Print all camera parameters.
        """
        print("Camera parameters:")
        print(f"  ROI: {self.roi}")
        print(f"  Exposure: {self.acqtime} ms")

    def set_roi(self, roi_tuple=(0, 0, 2048, 2048)):
        """
        Set camera ROI; expects a tuple: (HOffset, VOffset, Width, Height).
        """
        if isinstance(roi_tuple, list):
            try:
                roi_tuple = roi_tuple[0].split(',')
                roi_tuple = tuple([int(x) for x in roi_tuple])
            except ValueError:
                print("ROI values must be integers.")
        
        elif isinstance(roi_tuple, str):
            try:
                roi_tuple = roi_tuple.split(',')
                roi_tuple = tuple([int(x) for x in roi_tuple])
            except ValueError:
                print("ROI values must be integers.")

        if len(roi_tuple) != 4:
            print("ROI must be a 4-element tuple: (HOffset, VOffset, Width, Height)")
            return

        roi = TUCAM_ROI_ATTR()
        roi.bEnable = 1
        roi.nHOffset, roi.nVOffset, roi.nWidth, roi.nHeight = roi_tuple

        try:
            TUCAM_Cap_SetROI(self.TUCAMOPEN.hIdxTUCam, roi)
            print(
                "Set ROI success: HOffset={}, VOffset={}, Width={}, Height={}".format(
                    roi.nHOffset, roi.nVOffset, roi.nWidth, roi.nHeight
                )
            )
            
        except Exception as e:
            error_details = traceback.format_exc()
            result = f" > Error: {e}\n{error_details}"
            print(result)
            print(
                "Set ROI failure: HOffset={}, VOffset={}, Width={}, Height={}".format(
                    roi.nHOffset, roi.nVOffset, roi.nWidth, roi.nHeight
                )
            )

        self.roi = roi_tuple

    def export_data(self, data, filename='default', save_dir=None, overwrite=False):
        """
        Example data export, saves to <script_dir>/data by default.
        """
        if not save_dir:
            save_dir = os.path.join(self.script_dir, 'data')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        index = len([file for file in os.listdir(save_dir) if f'{filename}' in file])
        if overwrite is True:
            filename = f'{filename}.npy'
        else:
            filename = f'{filename}_{index}.npy'

        filepath = os.path.join(save_dir, filename)
        np.save(filepath, data)
        print('Data saved to %s' % filepath)

    def camera_info(self):
        """Prints the camera info obtained by get_camera_parameters."""
        if len(self.camera_parameters) == 0 or len(self.camera_capabilities) == 0:
            self.get_camera_parameters()

        print("Camera Parameters:")
        for key, parameters in self.camera_parameters.items():
            # print(f"  {key}: {value}")
            print(f"{key}:")
            for param_key, param_value in parameters.items():
                print(f"  {param_key}: {param_value}")

        print("\nCamera Capabilities:")
        for key, capabilities in self.camera_capabilities.items():
            # print(f"  {key}: {value}")
            print(f"{key}:")
            for cap_key, cap_value in capabilities.items():
                print(f"  {cap_key}: {cap_value}")
        

    def get_camera_parameters(self):
        """
        Retrieves and prints all available properties and capabilities of the camera.
        Handles unknown return values gracefully.
        """
        if not hasattr(self, "TUCAMOPEN") or self.TUCAMOPEN.hIdxTUCam == 0:
            print("Error: Camera not initialized or opened.")
            return

        print("\n=== Camera Properties ===")
        for prop in TUCAM_IDPROP:
            try:
                prop_attr = TUCAM_PROP_ATTR()
                prop_attr.idProp = prop.value
                status = TUCAM_Prop_GetAttr(self.TUCAMOPEN.hIdxTUCam, byref(prop_attr))

                if status == TUCAMRET.TUCAMRET_SUCCESS:
                    print(f"{prop.name}:")
                    print(f"  Min: {prop_attr.dbValMin}")
                    print(f"  Max: {prop_attr.dbValMax}")
                    print(f"  Default: {prop_attr.dbValDft}")
                    print(f"  Step: {prop_attr.dbValStep}")

                    # Save the parameters for later use
                    self.camera_parameters[prop.name] = {
                        "min": prop_attr.dbValMin,
                        "max": prop_attr.dbValMax,
                        "default": prop_attr.dbValDft,
                        "step": prop_attr.dbValStep
                    }

                else:
                    print(f"{prop.name}: Not Available (Error Code: {status})")

            except Exception as e:
                print(f"{prop.name}: Error - {str(e)}")

        print("\n=== Camera Capabilities ===")
        for capa in TUCAM_IDCAPA:
            try:
                capa_attr = TUCAM_CAPA_ATTR()
                capa_attr.idCapa = capa.value
                status = TUCAM_Capa_GetAttr(self.TUCAMOPEN.hIdxTUCam, byref(capa_attr))

                if status == TUCAMRET.TUCAMRET_SUCCESS:
                    print(f"{capa.name}:")
                    print(f"  Min: {capa_attr.nValMin}")
                    print(f"  Max: {capa_attr.nValMax}")
                    print(f"  Default: {capa_attr.nValDft}")
                    print(f"  Step: {capa_attr.nValStep}")

                    # Save the capabilities for later use
                    self.camera_capabilities[capa.name] = {
                        "min": capa_attr.nValMin,
                        "max": capa_attr.nValMax,
                        "default": capa_attr.nValDft,
                        "step": capa_attr.nValStep
                    }

                else:
                    print(f"{capa.name}: Not Available (Error Code: {status})")

            except Exception as e:
                print(f"{capa.name}: Error - {str(e)}")

        print(f"Camera Parameters: {len(self.camera_parameters)}")
        print(f"Camera Capabilities: {len(self.camera_capabilities)}")

    def get_gain_attributes(self):
        """
        Get the attributes for the camera gain, including min, max, default, and step values.

        :return: A dictionary with 'min', 'max', 'default', and 'step' values, or None if retrieval fails.
        """
        if not hasattr(self, "TUCAMOPEN") or self.TUCAMOPEN.hIdxTUCam == 0:
            print("Error: Camera not initialized or opened.")
            return None

        attr = TUCAM_PROP_ATTR()
        attr.idProp = TUCAM_IDPROP.TUIDP_GLOBALGAIN.value
        status = TUCAM_Prop_GetAttr(self.TUCAMOPEN.hIdxTUCam, byref(attr))

        if status == TUCAMRET.TUCAMRET_SUCCESS:
            return {
                "min": attr.dbValMin,
                "max": attr.dbValMax,
                "default": attr.dbValDft,
                "step": attr.dbValStep
            }
        else:
            print(f"Failed to get camera gain attributes. Error code: {status}")
            return None
    
    def set_gain(self, gain_value):
        """
        Set the camera gain within valid limits.

        :param gain_value: Desired gain value.
        """
        if not hasattr(self, "TUCAMOPEN") or self.TUCAMOPEN.hIdxTUCam == 0:
            print("Error: Camera not initialized or opened.")
            return

        gain_attrs = self.get_gain_attributes()
        if not gain_attrs:
            return

        min_gain, max_gain = gain_attrs["min"], gain_attrs["max"]
        
        if not (min_gain <= gain_value <= max_gain):
            print(f"Error: Gain value out of range! Must be between {min_gain} and {max_gain}.")
            return

        status = TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_GLOBALGAIN.value, gain_value, 0)

        if status == TUCAMRET.TUCAMRET_SUCCESS:
            print(f"Gain set to {gain_value} successfully.")
        else:
            print(f"Failed to set gain. Error code: {status}")

    def set_high_signal_boost(self):
        """
        Configures the camera for the highest signal boost by:
        - Setting Image Mode to HighGain, 12Bit(HighSpeed) (`IMGMODESELECT = 3`).
        - Setting Gain Level to 1 (`GLOBALGAIN = 1`).
        TODO: Come back and check if this is the best configuration for signal boost.
        """
        if not hasattr(self, "TUCAMOPEN") or self.TUCAMOPEN.hIdxTUCam == 0:
            print("Error: Camera not initialized or opened.")
            return

        # Set Image Mode to HighGain, 12Bit(HighSpeed) (`IMGMODESELECT = 3`)
        status_mode = TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDC_IMGMODESELECT.value, 3, 0)
        
        if status_mode == TUCAMRET.TUCAMRET_SUCCESS:
            print("Image mode set to HighGain, 12Bit(HighSpeed) (IMGMODE 3).")
        else:
            print(f"Failed to set image mode. Error code: {status_mode}")
            return

        # Set Gain Level to 1
        status_gain = TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_GLOBALGAIN.value, 1, 0)

        if status_gain == TUCAMRET.TUCAMRET_SUCCESS:
            print("Gain set to 1 (HighGain Mode).")
        else:
            print(f"Failed to set gain. Error code: {status_gain}")


    def calibrate_best_signal(self):
        """
        Tests all image mode and gain combinations to find the optimal configuration for maximum signal.

        - Iterates through all valid `TUIDC_IMGMODESELECT` and `TUIDP_GLOBALGAIN` values.
        - Captures a frame for each setting.
        - Analyzes signal strength (e.g., max intensity).
        - Returns the best combination based on measured signal.

        :return: Dictionary with the best image mode, gain, and measured signal.
        """
        if not hasattr(self, "TUCAMOPEN") or self.TUCAMOPEN.hIdxTUCam == 0:
            print("Error: Camera not initialized or opened.")
            return

        # Define all valid image modes and gain levels
        test_combinations = [
            {"img_mode": 1, "gain": 0, "desc": "CMS, 12Bit"},
            {"img_mode": 2, "gain": 0, "desc": "HDR, 16Bit"},
            {"img_mode": 2, "gain": 1, "desc": "HighGain, 11Bit"},
            {"img_mode": 3, "gain": 1, "desc": "HighGain, 12Bit(HighSpeed)"},
            {"img_mode": 5, "gain": 1, "desc": "HighGain, 12Bit(Global Reset)"},
            {"img_mode": 2, "gain": 2, "desc": "LowGain, 11Bit"},
            {"img_mode": 4, "gain": 2, "desc": "LowGain, 12Bit(HighSpeed)"},
            {"img_mode": 5, "gain": 2, "desc": "LowGain, 12Bit(Global Reset)"},
        ]

        best_config = None
        best_signal = -1  # Start with an impossible signal value

        for config in test_combinations:
            print(f"Testing {config['desc']} (Mode {config['img_mode']}, Gain {config['gain']})...")

            # Set image mode
            mode_status = TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDC_IMGMODESELECT.value, config["img_mode"], 0)
            if mode_status != TUCAMRET.TUCAMRET_SUCCESS:
                print(f"  Failed to set image mode {config['img_mode']}. Skipping...")
                continue

            # Set gain
            gain_status = TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_GLOBALGAIN.value, config["gain"], 0)
            if gain_status != TUCAMRET.TUCAMRET_SUCCESS:
                print(f"  Failed to set gain {config['gain']}. Skipping...")
                continue

            # Acquire a frame
            frame = self.acquire_one_frame()
            self.export_data(frame, f'{config["desc"]}_frame')
        #     if frame is None:
        #         print("  Failed to capture frame. Skipping...")
        #         continue

        #     # Measure signal strength (max pixel intensity)
        #     signal_strength = frame.max()
        #     print(f"  Measured Signal: {signal_strength}")

        #     # Track best setting
        #     if signal_strength > best_signal:
        #         best_signal = signal_strength
        #         best_config = config

        # print("\n** Best Configuration Found **")
        # if best_config:
        #     print(f"Mode: {best_config['desc']} (IMGMODE {best_config['img_mode']}), Gain {best_config['gain']}")
        #     print(f"Signal Strength: {best_signal}")
        # else:
        #     print("No valid configuration found!")

        # return best_config


    # ------------------
    # Internal Helpers
    # ------------------
    def _convert_to_numpy(self, frame):
        """
        Convert the frame buffer to a numpy array.
        """
        buf_type = ctypes.POINTER(ctypes.c_ubyte)
        buffer_ptr = ctypes.cast(frame.pBuffer, buf_type)
        buffer_list = list(buffer_ptr[:frame.uiImgSize])

        np_array = np.array(buffer_list, dtype=np.uint8)
        np_array = np_array.reshape((frame.usHeight, frame.usWidth, frame.ucElemBytes))
        return np_array

    # def get_camera_info(self):
    #     # Example stub if you have gain-attribute retrieval from TUCam
    #     gain_info = get_camera_gain_attributes(self.handle)
    #     print(gain_info)
    #     return gain_info
