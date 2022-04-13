import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pika.exchange_type import ExchangeType
import pika
import json
from time import sleep
import log.logger as logger
from basebroker import MessageBroker
import cloud4Rpi as cloudService
import sensehathandler as SenseHat

DEFAULT_QUEUE = "samples"


class RabbitMQConsumer(MessageBroker):
    ''' Class for rabbitMQ consumer

    '''

    def __init__(self, queue, on_msg_callback, path=None, **kwargs):
        ''' Class initialization

        :param queue: Name of queue
        :parm on_msg_callback: Callback for new messages
        :param path: Path to credentials file

        '''
        super(RabbitMQConsumer, self).__init__(queue, path, **kwargs)  # Base class initialization
        self._qos = kwargs.get('qos', 1)
        self._on_msg_callback = self.on_message
        self._allow_reconnect = False
        self.was_consuming = False
        self._consumer_tag = None
        self._consuming = False
        self._closing = False
        self._consumed = 0
        self._acked = 0
        self.sensehat = SenseHat.SenseHatHandler()
        self.cloud_service = cloudService.Cloud4RPi()
        self.reset_stats()

    def on_connection_open_error(self, connection, err):
        '''

        :param connection: The connection
        :param err: Error reason
        :return:
        '''
        logger.error('Failed to open connection. Reason={} Retrying in {}s ...'.format(err, DEFAULT_RETRY_TIMEOUT_SEC))
        self.reconnect()

    def on_connection_closed(self, connection, reason):
        ''' Callback method for connection closed

        :param connection: The connection
        :param reason: Reason whey connection was close
        :return:
        '''

        self._channel = None
        if self._shutdown:
            self._connection.ioloop.stop()
        else:
            logger.warning(
                'Connection closed. Reason={} Reopening in {}s ...'.format(reason, DEFAULT_RETRY_TIMEOUT_SEC))
            self._connection.ioloop.call_later(DEFAULT_RETRY_TIMEOUT_SEC, self._connection.ioloop.stop)

    def reconnect(self):
        ''' Will attempt to establish connect after closed

        :return:
        '''

        self._allow_reconnect = False
        self.stop()

    def on_connection_closed(self, connection, reason):
        ''' Callback method for connection closed

        :param connection: The connection
        :param reason: Reason whey connection was close
        :return:
        '''

        self._channel = None
        if self._shutdown:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed. Reason={} Reconnecting ...')
            self.reconnect()

    def on_queue_ok(self, userdata):
        ''' Callback for queue declaration

        :param frame:
        :param userdata:
        :return:
        '''

        if self._bind_required:
            self._bind_required = False
            logger.info('Binding exchange = "{}" to queue = "{}" using route key = "{}"')
            self._channel.queue_bind(self._queue_name, self._exchange, routing_key=self._route_key,
                                     callback=self.on_bind_ok)
        else:
            self.set_qos()

    def on_bind_ok(self, frame, userdata):
        ''' Callback for bind ok

        :param frame: Frame response
        :param userdata: User data
        :return:
        '''
        logger.info('Queue "{}" bounded'.format(self._queue_name))
        self.set_qos()

    def set_qos(self):
        ''' Sets the number of message to fetch per request

        :return:
        '''
        logger.info('Setting qos to {}'.format(self._qos))
        self._channel.basic_qos(prefetch_count=self._qos, callback=self.on_qos_ok)

    def on_qos_ok(self, frame):
        ''' Callback for qos ok

        :param frame: Frame response
        :return:
        '''
        logger.info('QOS set to {}'.format(self._qos))
        self.start_consuming()

    def start_consuming(self):
        ''' Sets up consume cancellations and on message callback

        :return:
        '''

        logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

        # setup callback for message fetched
        self._consumer_tag = self._channel.basic_consume(self._queue_name, self.on_message)
        self.was_consuming = True
        self._consuming = True
        logger.info('Ready to consume messages')

    def on_consumer_cancelled(self, frame):
        ''' Callback for consumer cancellation

        :param frame:
        :return:
        '''
        logger.info('Consumer cancelled, shutting down: {}', frame)
        if self._channel:
            self._channel.close()

    def on_message(self, channel, basic_deliver, properties, body):
        ''' Callback for received message

        :param channel: Channel object
        :param basic_deliver: Delivery method
        :param properties: Properties
        :param body: Message body
        :return:
        '''
        logger.info('Received message: exchange = "{}" route key = "{}" tag = {} '.format(
            basic_deliver.exchange, basic_deliver.routing_key, basic_deliver.delivery_tag))
        logger.debug('Body = {}'.format(body))
        self._consumed += 1
        self.acknowledge_message(basic_deliver.delivery_tag)
        msg = body.decode()
        self.log_rx(msg)
        
        try:
            res = json.loads(msg)
            temperature = res["temperature"]
            humidity = res["humidity"]
            pressure = res["pressure"]

            self.cloud_service.send_sensor_update(temperature, humidity, pressure)
            accel = [res["acceleration"]["pitch"], res["acceleration"]["roll"], res["acceleration"]["yaw"]]
            orient = [res["orientation"]["pitch"], res["orientation"]["roll"], res["orientation"]["yaw"]]
            compass = res["compass"]
            
            self.sensehat.update_led_values(accel, compass, orient)

        except:
            logger.error('Message received is not in JSON format')


    def acknowledge_message(self, delivery_tag):
        ''' Acknowledge the message delivery

        :param delivery_tag: Delivery tag
        :return:
        '''
        logger.info('Acknowledging message tag = {}'.format(delivery_tag))
        self._channel.basic_ack(delivery_tag)
        self._acked += 1

    def stop_consuming(self):
        ''' Tell server to stop consuming

        :return:
        '''
        if self._channel:
            logger.info('Sending consume stop to server ...')
            self._channel.basic_cancel(self._consumer_tag, self.on_cancel_ok)

    def on_cancel_ok(self, frame, userdata):
        ''' Callback for consume stop

        :param frame: Frame response
        :param userdata: User data
        :return:
        '''

        self._consuming = False
        logger.info('RabbitMQ acknowledged the cancellation of the consumer: {}'.format(userdata))
        self.close_channel()

    def run(self):
        ''' Override for threading start()

        :return:
        '''

        logger.info("Consumer thread started")

        while not self._shutdown:

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except:
                break

        logger.info("Consumer thread stopped")

    def stop(self):
        ''' Stop server

        :return:
        '''
        # If there is no data being received, close socket the for exception
        if not self._closing:
            self._shutdown = True
            self._closing = True
            logger.info('Stopping consumer ...')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.stop()
            else:
                self._connection.ioloop.start()
            logger.info('Consumer stopped')

    def reset_stats(self):
        ''' Reset message stats

                :return:
                '''
        self._consumed = 0
        self._acked = 0

class RabbitMQProducer(MessageBroker):
    '''
    Class for rabbitMQ producer
    '''

    def __init__(self, queue, path=None, **kwargs):
        ''' Class initialization

        :param queue: Name of queue
        :param path: Path to credentials file
        '''
        super(RabbitMQProducer, self).__init__(queue, path, **kwargs)  # Base class initialization
        self._publish_count = None
        self._ack = None
        self._nack = None
        self.reset_stats()

    def on_queue_ok(self, userdata):
        ''' Callback for queue declaration

        :param frame:
        :param userdata:
        :return:
        '''

        name = userdata.method.queue
        logger.info('Queue "{}" declared'.format(name))
        self.enable_delivery_confirmation()

    def enable_delivery_confirmation(self):
        ''' Enabled publish confirmations
        '''
        logger.info('Enabling delivery confirmation for {}'.format(self._queue_name))
        self._channel.confirm_delivery(self.on_delivery_confirmation)

        logger.info('Ready to publish')
        self._ready = True

    def on_delivery_confirmation(self, frame):
        ''' Call back for delivery confirmations

        :param frame: Confirmation response
        :return:
        '''

        ack_type = frame.method.NAME.split('.')[1].lower()
        logger.info('Received {} for delivery tag: {}'.format(ack_type, frame.method.delivery_tag))
        if ack_type == 'ack':
            self._ack += 1
        elif ack_type == 'nack':
            self._nack += 1
        self.print_stats()

    def publish(self, data):
        if not self._ready:
            return self._ready

        self._publish_count += 1
        logger.info('Publishing message #{}'.format(self._publish_count))
        json_str = json.dumps(data)
        self._channel.basic_publish(exchange=self._exchange, routing_key=self._route_key, body=json_str)
        self.print_stats()
        return self._ready

    def reset_stats(self):
        ''' Reset message stats

        :return:
        '''
        self._publish_count = 0
        self._ack = 0
        self._nack = 0

    def print_stats(self):
        ''' Display message stats

        :return:
        '''
        logger.debug('Messages: publish={}, acked={}, nacked={}'.format(self._publish_count, self._ack, self._nack))

    def run(self):
        logger.info("Producer thread started")

        while not self._shutdown:
            self._connection = None

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except Exception as e:
                logger.info("Stopping producer ...")
                self._shutdown = True
                if (self._connection is not None and not self._connection.is_closed):
                    # Finish closing
                    self._connection.ioloop.start()
                break

        logger.info("Producer thread stopped")

    def stop(self):
        ''' Stop the producer

        :return:
        '''

        logger.info("Stopping producer ...")
        self._shutdown = True
        self.close_channel()
        self.close_connection()
