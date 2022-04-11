#!/usr/bin/env python3

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
Date        : 30 March 2022
Version     : 1.0

Description : Main sense hat live project

Reference   :
------------------------------------------------------------------------------------------------------------------------
"""

import os
import argparse
import signal
import sys
import threading
import time
import json

import log.logger as logger
import rabbitmq as mq
broker = None

def sig_handler(signum=None, frame=None):
    ''' Signal handler

    :param signum: Signal responsible for call back
    :return:
    '''
    if signum is not None:
        logger.info("Signal %i caught, exiting...", signum)

    # Clear exit
    sys.exit()


def main(args):
    global broker

    rc = 0

    # Register signals, such as CTRL + C and GUI close
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    # Initialize the logger
    logger.initLogger(console=not args.quiet, log_dir=False, verbose=args.verbose)
    
    # Create a new broker
    broker = None
    if args.consumer:
        broker_type = 'Consumer'
        broker = mq.RabbitMQConsumer(queue='samples',on_msg_callback=None)
    else:
        broker_type = 'Producer'
        broker = mq.RabbitMQProducer(queue='samples')

    broker.start()


    try:
        logger.info("Sense Hat Live!: {}".format(broker_type))
    
        if broker_type == 'Producer':
            while True:
                try:
                    orientation = {'pitch': 2, 'roll': 3, 'yaw': 4}
                    accelerometer = {'pitch': 7, 'roll': 6, 'yaw': 5}
                    
                    data = {
                    "temperature": 75,
                    "humidity": 20,
                    "pressure": 44,
                    "compass": 200,
                    "acceleration": accelerometer,
                    "orientation": orientation
                    }
#            json_str = json.dumps(data)
                    success = broker.publish(data)
                    if success:
                        print("successfully sent")
                    else:
                        print("failed to send")
                    time.sleep(10)

                except Exception as e:
                    logger.error(str(e))
                    break
        if broker_type == 'Consumer':
            while True:
                pass
        
    except Exception as e:
        logger.error('Exception caught: ' + str(e))

    sys.exit(rc)

if __name__ == '__main__':
    # KJ - Adding command line arguments to allow selection of UI
    parser = argparse.ArgumentParser(description='Super project launcher')


    parser.add_argument('-c', '--consumer', action="store_true", default=False,
                        help='Run in consumer mode')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase console logging verbosity')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Turn off console logging')
    args = parser.parse_args()

    main(args)
