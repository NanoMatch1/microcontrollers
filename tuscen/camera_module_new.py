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
    

)

# from TUCam import get_camera_gain_attributes    # If you have a local function to retrieve gain info

class TucamCamera:
    """
    A refactored camera class that encapsulates initialization,
    acquisition, and teardown for a Tucsen camera.
    """

    def __init__(self, interface=None):
        """
        Initialize the camera driver (but do not open a specific camera yet).
        """
        self.interface = interface
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.transient_dir = self.interface.transientDir if self.interface else self.script_dir

        # acquisition parameters
        self.acq_time = 100 # milliseconds
        self.roi = (0, 0, 2048, 2048)


        # Thread-safety and acquisition flags
        self.camera_lock = threading.Lock()
        self.stop_flag = threading.Event()
        self.is_running = False

        print('Print finished TucsenCamera init')

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




    def open_camera(self, Idx=0):

        if  Idx >= self.TUCAMINIT.uiCamCount:
            return

        print('Opening camera...')
        self.TUCAMOPEN = TUCAM_OPEN(Idx, 0)

        # ch:打开相机Idx | en:Open camera Idx
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
        # self.set_exposure(200)

        data_dict = self.wait_for_image_data(nframes=1)
        # self.close_camera()
        if export is True:
            self.export_data(data_dict[0], 'test')
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
            self.open_camera(0)
            self.set_roi(roi)
            self.set_exposure(exposure)

            while not self.stop_flag.is_set():
                try:
                    with self.camera_lock:
                        data_dict = self.wait_for_image_data(nframes=1)
                    if not data_dict:
                        continue
                    data = data_dict[0]
                    file_path = os.path.join(self.transient_dir, "transient_data.npy")
                    np.save(file_path, data)
                    time.sleep(0.001)
                except Exception as e:
                    print(f"Acquisition error: {e}")
                    break

            self.close_camera()

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

    def wait_for_image_data(self, nframes=10):
        """
        Core logic to wait for camera frames and convert them to numpy arrays.
        Returns a dictionary {frame_index: frame_data}.
        """
        data_dict = {}

        m_frame = TUCAM_FRAME()
        m_frame.pBuffer = 0
        m_frame.ucFormatGet = TUFRM_FORMATS.TUFRM_FMT_USUAl.value
        m_frame.uiRsdSize = 1

        # Allocate internal buffer
        TUCAM_Buf_Alloc(self.TUCAMOPEN.hIdxTUCam, pointer(m_frame))
        # Start capturing in sequence mode
        TUCAM_Cap_Start(self.TUCAMOPEN.hIdxTUCam, TUCAM_CAPTURE_MODES.TUCCM_SEQUENCE.value)

        for i in range(nframes):
            try:
                # Wait for the next frame
                _ = TUCAM_Buf_WaitForFrame(self.TUCAMOPEN.hIdxTUCam, pointer(m_frame), 1000)
                print(
                    "Frame index: {}, width: {}, height: {}, channels: {}, elembytes: {}, size: {}".format(
                        i, m_frame.usWidth, m_frame.usHeight,
                        m_frame.ucChannels, m_frame.ucElemBytes, m_frame.uiImgSize
                    )
                )
            except Exception:
                print("Grab the frame failure, index number is {}".format(i))
                continue

            # Convert to numpy
            try:
                data = self._convert_to_numpy(m_frame)
                data_dict[i] = data
            except Exception as e:
                print(e)
                print("Convert to numpy failed for frame ", i)
                continue

        # Stop capturing and release buffer
        TUCAM_Buf_AbortWait(self.TUCAMOPEN.hIdxTUCam)
        TUCAM_Cap_Stop(self.TUCAMOPEN.hIdxTUCam)
        TUCAM_Buf_Release(self.TUCAMOPEN.hIdxTUCam)

        return data_dict

    def set_exposure(self, value):
        """
        Set camera exposure time to 'value' (in microseconds or ms—depends on the camera).
        """
        TUCAM_Capa_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDCAPA.TUIDC_ATEXPOSURE.value, 0)
        TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_EXPOSURETM.value, value, 0)
        print(f"Set exposure to {value}")

    def set_roi(self, roi_tuple=(0, 0, 2048, 2048)):
        """
        Set camera ROI; expects a tuple: (HOffset, VOffset, Width, Height).
        """
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

    def export_data(self, data, filename='default'):
        """
        Example data export, saves to <script_dir>/data by default.
        """
        save_dir = os.path.join(self.script_dir, 'data')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        index = len([file for file in os.listdir(save_dir) if f'{filename}' in file])
        filename = f'{filename}_{index}.npy'

        filepath = os.path.join(save_dir, filename)
        np.save(filepath, data)
        print('Data saved to %s' % filepath)

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
