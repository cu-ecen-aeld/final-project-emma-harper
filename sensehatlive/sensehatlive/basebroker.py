#!/usr/bin/env python3

"""
------------------------------------------------------------------------------------------------------------------------
File Name   : basebroker.py
Author      : Kenneth A. Jones
              Spring 2022
              AESD
              University of Colorado Boulder
Email       : kenneth.jones@colorado.edu
Platform    : Linux VM (32/64 Bit)
IDE Used    : Visual Studio Code IDE
Date        : 6 March 2022
Version     : 1.0

Description : Base class for message broker

Reference   :
------------------------------------------------------------------------------------------------------------------------
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import threading
import pika
import json
import log.logger as logger
from pika.exchange_type import ExchangeType

# Default location for credential file
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_RETRY_TIMEOUT_SEC = 5



class MessageBroker(threading.Thread):
    ''' Base class for message broker

    '''

    def __init__(self, queue_name, path, **kwargs):
        '''

        :param queue_name: Name of queue
        :param path: Path to credentials file
        '''
        super(MessageBroker, self).__init__()  # Base class initialization
        self._connection = None
        self._shutdown = False
        self._queue_name = queue_name
        self._exchange = kwargs.get('exchange', '')
        self._exchange_type = kwargs.get('exchange_type', ExchangeType.direct)
        self._route_key = kwargs.get('route_key', queue_name)
        self._bind_required = False
        self._ready = False
        self._channel = None
        self._config = self.load_config(DEFAULT_PATH if path is None else path)

    def load_config(self, path):
        ''' Loads RabbitMQ connection parameters if present or creates

        :return:
        '''
        if not os.path.exists(path):
            raise Exception("The credential file does not exist, please create.")

        try:
            with open(path) as f:
                data = json.load(f)
                logger.debug('Message broker config successfully loaded')
                return data
        except Exception as e:
            raise Exception(str(e))

    def connect(self):
        ''' Establish connection with the RabbitMQ server

        :return:
        '''
        url = self._config.get('url')
        if url is None:
            credentials = pika.PlainCredentials(self._config.get('username'), self._config.get('password'))
            parameters = pika.ConnectionParameters(host=self._config.get('host'),
                                                   virtual_host=self._config.get('virtual_host'),
                                                   credentials=credentials)
        else:
            parameters = pika.URLParameters(url)

        return pika.SelectConnection(parameters,
                                     on_open_callback=self.on_connection_open,
                                     on_open_error_callback=self.on_connection_open_error,
                                     on_close_callback=self.on_connection_closed)

    def on_connection_open(self, connection):
        '''

        :param connection: The connection
        :return:
        '''

        logger.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, connection, err):
        '''

        :param connection: The connection
        :param err: Error reason
        :return:
        '''
        logger.error('Failed to open connection. Reason={} Retrying in {}s ...'.format(err, DEFAULT_RETRY_TIMEOUT_SEC))
        self._connection.ioloop.call_later(DEFAULT_RETRY_TIMEOUT_SEC, self._connection.ioloop.stop)  # Retry open

    def on_connection_closed(self, connection, reason):
        ''' Callback method for connection closed

        :param connection: The connection
        :param reason: Reason whey connection was close
        :return:
        '''

        self._channel = None
        self._ready = False
        if self._shutdown:
            self._connection.ioloop.stop()
        else:
            logger.warning(
                'Connection closed. Reason={} Reopening in {}s ...'.format(reason, DEFAULT_RETRY_TIMEOUT_SEC))
            self._connection.ioloop.call_later(DEFAULT_RETRY_TIMEOUT_SEC, self._connection.ioloop.stop)

    def close_connection(self):
        ''' Close connection with RabbitMQ

        :return:
        '''

        if self._connection is not None:
            logger.info('Closing connection ...')
            self._connection.close()

    def open_channel(self):
        ''' Opens channel with the RabbitMQ server

        :return:
        '''

        self._connection.channel(on_open_callback=self.on_channel_open)

    def close_channel(self):
        ''' Closes channel

        :return:
        '''
        if self._channel is not None:
            logger.info('Closing the channel ...')
            self._channel.close()

    def on_channel_open(self, channel):
        ''' Callback for channel opened

        :param channel: The channel
        :return:
        '''

        logger.info('Channel {} opened'.format(channel.channel_number))
        self._channel = channel  # Save channel
        self._channel.add_on_close_callback(self.on_channel_closed)  # Add callback for channel closed

        # Just setup the queue when a valid exchange or route key has not been provided
        if self._exchange is None or self._exchange == '' or self._route_key is None or self._route_key == '':
            self._route_key = self._queue_name  # Using direct mode route key must equal queue name
            self.setup_queue()
        else:
            self._bind_required = True
            self.setup_exchange()

    def on_channel_closed(self, channel, reason):
        """ Callback to handle channel closed

        :param channel: The channel
        :param reason: Reason channel was closed
        :return:
        """

        logger.warning('Channel {} was closed. Reason={}'.format(channel.channel_number, reason))
        self._ready = False
        self._channel = None

        if not self._shutdown:
            self._connection.close()

    def setup_exchange(self):
        ''' Sets up the exchange

        :return:
        '''
        logger.info('Declaring exchange = "{}" ....'.format(self._exchange))
        self._channel.exchange_declare(exchange=self._exchange, exchange_type=self._exchange_type,
                                       callback=self.on_exchange_ok)

    def on_exchange_ok(self, frame, userdata):
        logger.info('Exchange "{}" declared'.format(userdata))
        self.setup_queue()

    def setup_queue(self):
        ''' Setup a queue

        :return:
        '''

        logger.info('Declaring queue "{}"'.format(self._queue_name))
        self._channel.queue_declare(queue=self._queue_name, callback=self.on_queue_ok)

    def on_queue_ok(self, userdata):
        ''' Callback for queue declaration

        :param frame:
        :param userdata:
        :return:
        '''
        raise Exception('on_queue_ok() Not Implemented')

    def on_bind_ok(self, frame, userdata):
        ''' Callback for bind ok

        :param frame: Frame response
        :param userdata: User data
        :return:
        '''
        raise Exception('on_bind_ok() Not Implemented')

    def run(self):
        """ Stars the message broker server

        :return:
        """
        raise Exception('Not Implemented')

    def stop(self):
        """ Stop message broker server

        :return:
        """
        raise Exception('stop() Not Implemented')

    def log_rx(self, message):
        """ Logs received message

        :param message: Message received
        :return:
        """
        logger.info('Rx: {}'.format(message))

    def log_tx(self, message):
        """ Logs transmitted message

        :param message: Message transmitted
        :return:
        """
        logger.info('Tx: {}'.format(message))

    def reset_stats(self):
        ''' Reset message stats

        :return:
        '''
        raise Exception('reset_stats() Not Implemented')
