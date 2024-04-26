#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import sys
import os
import RPi.GPIO as GPIO
from PIL import Image, ImageFont, ImageDraw
from inky.auto import auto
from font_source_serif_pro import SourceSerifProSemibold
from font_source_sans_pro import SourceSansProSemibold

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
Button = 4
GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize Inky Display
inky_display = auto(ask_user=True, verbose=True)
inky_display.set_border(inky_display.WHITE)

def display_quote():
    # Existing quote display code goes here
    # Ensure you are using the inky_display variable
    pass

def display_image(image_path):
    # Function to display an image
    img = Image.open(image_path)
    img = img.resize((inky_display.width, inky_display.height))
    inky_display.set_image(img)
    inky_display.show()

# Main loop
while True:
    if GPIO.input(Button) == GPIO.HIGH:
        print("Button Pushed")
        if random.choice([True, False]):
            display_quote()
        else:
            # Replace 'path_to_your_image.jpg' with the path to your image
            display_image('path_to_your_image.jpg')
