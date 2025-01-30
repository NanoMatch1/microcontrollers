#!/usr/bin/env python
# coding: utf-8

import time
from microcontrollers.tuscen.tucsen_camera_real import TucamCamera
import traceback

def cli(camera):
    print("Camera CLI started. Enter 'help' for available commands.")

    def parse_input(input_str):
        try:
            command_strip = input_str.split(' ')
            if len(command_strip) == 1:
                return command_strip[0], []
            else:
                # argss = tuple([tuple(x.split(',')) for x in command_strip[1:]]) if ',' in command_strip[1] else tuple(command_strip[1:])
                # return command_strip[0], argss
                return command_strip[0], command_strip[1:]
        except ValueError:
            return
    
    def show_help(camera):
        print("Available commands:")
        for command, method in camera.command_functions.items():
            print(f"{command} - {method.__doc__}")


    while True:
        user_input = input("Command: ").strip().lower()
        if user_input == 'help':
            show_help(camera)
            continue

        elif user_input == 'q' or user_input == 'exit':
            print("Exiting CLI...")
            break

        command, argss = parse_input(user_input)
        try:
            camera.command_functions[command](*(argss or []))
            continue
        except KeyError:
            print("Invalid command:{}\n Type 'help' for a list of commands.".format(user_input))
        except Exception as e:
            print(f"An error occurred: {traceback.format_exc()}")
            continue
        

if __name__ == '__main__':
    camera = TucamCamera(report=True)
    camera.initialise()
    
    try:
        cli(camera)
    except Exception as e:
        print("An error occurred:", e)
        print("Exiting CLI...")
    
    camera.uninit_api()
    print("Camera API uninitialized. Goodbye!")
