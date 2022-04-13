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
    ''' Class for rabbitMQ consumer

    '''
    DIRECTION_MOD = 22.5

    def __init__(self):
        # Class initialization
        self.sense = SenseHat()
        self.sense.clear()
        self.compass_strings = ['N', 'NNE', 'NE', 'ENE', 'E',
                            'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW',
                            'WSW', 'W', 'WNW', 'NW', 'NNW'
                            ]
        self.accel = [0,0,0]
        self.compass = 'N'
        self.orientation = [0,0,0]
        self.e = threading.Event()
        self.led_thread = threading.Thread(target=self.led_screen)
       # self.e.set()
        self.led_thread.start()

    def led_screen(self):
        blue = (0, 0, 255)
        while True:
            #event_is_set = self.e.wait()
            self.sense.show_message("accel: R:" + str(self.accel[0]) + 
                                        " P:" + str(self.accel[1])+ 
                                        " Y:" + str(self.accel[2]),
                                        text_colour=blue, scroll_speed=.05)
            self.sense.show_message("compass: " + self.compass,
                                        text_colour=blue, scroll_speed=.05)
            self.sense.show_message("orient: R:" + str(self.orientation[0]) + 
                                        " P:" + str(self.orientation[1])+ 
                                        " Y:" + str(self.orientation[2]),
                                        text_colour=blue, scroll_speed=.05)
            #self.e.clear()
            #self.sense.show_message("Pressure: " + str(self.pressure), text_color=blue, scroll_speed=0.5)     

    def update_led_values(self, accel, compass, orientation):

        self.accel[0] = accel[0]
        self.accel[1] = accel[1]
        self.accel[2] = accel[2]
        
        ix = int((compass + 11.25)/22.5)
        self.compass = self.compass_strings[ix % 16]

        self.orientation[0] = orientation[0]
        self.orientation[1] = orientation[1]
        self.orientation[2] = orientation[2]      
        #self.e.set()
