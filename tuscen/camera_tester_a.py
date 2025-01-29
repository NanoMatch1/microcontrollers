#!/usr/bin/env python
# coding: utf-8

import time
from camera_module_new import TucamCamera

def cli(camera):
    print("Camera CLI started. Enter 'help' for available commands.")
    
    while True:
        user_input = input("Command: ").strip().lower()
        
        if user_input == 'q' or user_input == 'exit':
            print("Exiting CLI...")
            break
        
        elif user_input == 'acquire':
            print("Acquiring single frame...")
            frame_data = camera.acquire_one_frame()
            if frame_data is not None:
                print("Frame acquired with shape:", frame_data.shape)
            else:
                print("Failed to acquire frame.")
                
        elif user_input == 'run':
            print("Starting continuous acquisition...")
            camera.start_continuous_acquisition(roi=(0, 1100, 2048, 400), exposure=200)
            
        elif user_input == 'stop':
            print("Stopping continuous acquisition...")
            camera.stop_continuous_acquisition()
            
        elif user_input == 'refresh':
            print("Refreshing camera...")
            camera.refresh()

        elif user_input.startswith('roi '):
            try:
                roi = tuple(map(int, user_input[4:].split(',')))
                camera.set_roi(roi)
                print("ROI set to:", roi)
            except Exception as e:
                print("Invalid ROI format. Please enter 4 integers separated by commas.")

        elif user_input.startswith('exposure '):
            try:
                exposure = int(user_input[9:])
                camera.set_exposure(exposure)
                print("Exposure set to:", exposure)
            except Exception as e:
                print("Invalid exposure value. Please enter an integer.")

        elif user_input == "gain info":
            gain_info = camera.get_gain_attributes()
            if gain_info:
                print(f"Gain range: {gain_info['min']} to {gain_info['max']}, Default: {gain_info['default']}, Step: {gain_info['step']}")

        elif user_input.startswith("gain "):
            try:
                gain_value = float(user_input.split()[1])
                camera.set_gain(gain_value)
            except (IndexError, ValueError):
                print("Usage: gain <value> (numeric value required)")


            
        elif user_input == 'help':
            print("Available commands:")
            print("  acquire - Capture a single frame")
            print("  run     - Start continuous acquisition")
            print("  stop    - Stop continuous acquisition")
            print("  refresh - Restart the camera driver")
            print("  exit/q  - Quit the CLI")
        
        else:
            print("Invalid command. Type 'help' for a list of commands.")

if __name__ == '__main__':
    camera = TucamCamera()
    camera.initialise()
    
    try:
        cli(camera)
    except Exception as e:
        print("An error occurred:", e)
        print("Exiting CLI...")
    
    camera.uninit_api()
    print("Camera API uninitialized. Goodbye!")
