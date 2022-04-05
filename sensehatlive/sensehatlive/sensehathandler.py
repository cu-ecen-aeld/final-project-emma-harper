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

    def __init__(self):
        # Class initialization
        self.sense = SenseHat()
        self.sense.clear()
        self.pressure = 0
        self.accel = [0,0,0]
        self.gyro = [0,0,0]
        self.mag = [0,0,0]
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
            self.sense.show_message("gyro:(" + str(self.gyro[0]) + 
                                        "," + str(self.gyro[1])+ 
                                        "," + str(self.gyro[2]) + ")",
                                        text_colour=blue, scroll_speed=.05)
            self.sense.show_message("mag:(" + str(self.mag[0]) + 
                                        "," + str(self.mag[1])+ 
                                        "," + str(self.mag[2]) + ")",
                                        text_colour=blue, scroll_speed=.05)
            #self.e.clear()
            #self.sense.show_message("Pressure: " + str(self.pressure), text_color=blue, scroll_speed=0.5)     

    def update_led_values(self, pressure, accel, gyro, magnitue):
        print("in handler")
        self.pressure = pressure
        self.accel[0] = accel[0]
        self.accel[1] = accel[1]
        self.accel[2] = accel[2]
        self.gyro[0] = gyro[0]
        self.gyro[1] = gyro[1]
        self.gyro[2] = gyro[2]
        self.mag[0] = magnitue[0]
        self.mag[1] = magnitue[1]
        self.mag[2] = magnitue[2]
        #self.e.set()
