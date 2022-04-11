"""
------------------------------------------------------------------------------------------------------------------------
File Name   : superproject.py
Author      : Emma Harper
              Spring 2022
              AESD
              University of Colorado Boulder
Email       : emha1608@colorado.edu
Platform    : Linux VM (32/64 Bit), Raspberry Pi 3B
IDE Used    : Visual Studio Code IDE
Date        : 01 April 2022
Version     : 1.0

Description : Sense Hat manager

Reference   :
------------------------------------------------------------------------------------------------------------------------
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pika
import json
import log.logger as logger
import RPi.GPIO as GPIO  # pylint: disable=F0401
from sense_hat import SenseHat
import threading
from time import sleep

class SenseHatHandler():
    ''' Class for Sense Hat management

    '''

    def __init__(self):
        # Class initialization
        self.sense = SenseHat()
        self.sense.clear()
        self.pressure = 0
        self.accel = [0,0,0]
        self.compass = 0
        self.orientation = [0,0,0]
        self.e = threading.Event()
        self.led_thread = threading.Thread(target=self.led_screen)
       # self.e.set()
        self.led_thread.start()

    def led_screen(self):
        blue = (0, 0, 255)
        while True:
            #event_is_set = self.e.wait()
            self.sense.show_message("Psi:" + str(self.pressure), text_colour=blue, scroll_speed=.05)     
            self.sense.show_message("accel:(" + str(self.accel[0]) + 
                                        "," + str(self.accel[1])+ 
                                        "," + str(self.accel[2]) + ")",
                                        text_colour=blue, scroll_speed=.05)
            self.sense.show_message("compass: " + str(self.compass),
                                        text_colour=blue, scroll_speed=.05)
            self.sense.show_message("orient:(" + str(self.orientation[0]) + 
                                        "," + str(self.orientation[1])+ 
                                        "," + str(self.orientation[2]) + ")",
                                        text_colour=blue, scroll_speed=.05)
            #self.e.clear()
            #self.sense.show_message("Pressure: " + str(self.pressure), text_color=blue, scroll_speed=0.5)     

    def update_led_values(self, pressure, accel, compass, orientation):
        print("in handler")
        self.pressure = pressure
        self.accel[0] = accel[0]
        self.accel[1] = accel[1]
        self.accel[2] = accel[2]
        self.compass = compass
        
        self.orientation[0] = orientation[0]
        self.orientation[1] = orientation[1]
        self.orientation[2] = orientation[2]      
        #self.e.set()
