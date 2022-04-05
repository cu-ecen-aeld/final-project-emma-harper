# -*- coding: utf-8 -*-

from time import sleep
import sys
import random
import cloud4rpi

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = 'fxqKDBvmweTLQgSFh5821w3g'


# Change these values depending on your requirements.
DATA_SENDING_INTERVAL = 60  # secs
DIAG_SENDING_INTERVAL = 650  # secs
POLL_INTERVAL = 0.5  # 500 ms



class Cloud4RPi():

    def __init__(self):
        self.device = cloud4rpi.connect(DEVICE_TOKEN)
        self.variables = {

            'temperature': {
                'type': 'numeric',
                'bind': self.get_temperature
            },
            'humidity': {
                'type': 'numeric',
                'bind': self.get_humidity
            },
        
        }
        self.device.declare(self.variables)
        self.device.publish_config()
        self.temperature = 0
        self.humidity = 0
        
    def get_temperature(self):
        return self.temperature
    
    def get_humidity(self):
        return self.humidity

    def send_sensor_update(self, temperature, humidity):
        # Put variable declarations here
        # Available types: 'bool', 'numeric', 'string', 'location'
        print(temperature)
        print(humidity)
        self.temperature = temperature
        self.humidity = humidity

        try:

            self.device.publish_data()


        except Exception as e:
            error = cloud4rpi.get_error_message(e)
            cloud4rpi.log.exception("ERROR! %s %s", error, sys.exc_info()[0])

        return


