#!/usr/bin/env python
# coding: utf-8

# main_script.py

from camera_module_new import TucamCamera

if __name__ == '__main__':
    # Instantiate
    camera = TucamCamera()

    # Optional: refresh the camera if needed
    camera.refresh()

    # Acquire one frame
    frame_data = camera.acquire_one_frame()
    if frame_data is not None:
        print("Got single frame of shape:", frame_data.shape)
    else:
        print("Failed to get single frame.")

    # Start continuous acquisition in a background thread
    camera.start_continuous_acquisition(roi=(0, 1100, 2048, 400), exposure=200)
    # Let it run for a few seconds
    import time
    time.sleep(2)
    # Stop
    camera.stop_continuous_acquisition()

    # Uninit the API at the very end
    camera.uninit_api()
