#!/usr/bin/env python

"""
 @Company
    NVNC Technology, LLC

 @Programmer(s)
    Kenneth A. Jones II

Copyright (C) NVNC Technology, LLC, 2017 All Rights Reserved. This code may not be copied
without the express written consent of NVNC Technology, LLC.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR
A PARTICULAR PURPOSE.

"""

import os
import sys
import multiprocessing
import contextlib
import threading
import traceback
import logging
import errno

from logging import handlers
from logutils.queue import QueueHandler, QueueListener

# These settings are for file log only
FILENAME = "sensehatlive.log"
MAX_SIZE = 1000000  # 1 MB
MAX_FILES = 5

# logger
logger = logging.getLogger("SenseHatLive")

# Global queue for multiprocessing log
queue = None


class LogListHandler(logging.Handler):
    """
    Log handler for Web UI.
    """

    def emit(self, record):
        message = self.format(record)
        message = message.replace("\n", "<br />")

        # hmi.LOG_LIST.insert(0, (helpers.now(), message, record.levelname, record.threadName))


@contextlib.contextmanager
def listener():
    """
    Wrapper that create a QueueListener, starts it and automatically stops it.
    To be used in a with statement in the main process, for multiprocessing.
    """

    global queue

    # Initialize queue if not already done
    if queue is None:
        try:
            queue = multiprocessing.Queue()
        except OSError as e:
            queue = False

            # Some machines don't have access to /dev/shm. See
            # http://stackoverflow.com/questions/2009278 for more information.
            if e.errno == errno.EACCES:
                logger.warning("Multiprocess log disabled, because "
                               "current user cannot map shared memory. You won't see any"
                               "log generated by the worker processed.")

    # Multiprocess log may be disabled.
    if not queue:
        yield
    else:
        queue_listener = QueueListener(queue, *logger.handlers)

        try:
            queue_listener.start()
            yield
        finally:
            queue_listener.stop()


def initMultiprocessing():
    """
    Remove all handlers and add QueueHandler on top. This should only be called
    inside a multiprocessing worker process, since it changes the logger
    completely.
    """

    # Multiprocess log may be disabled.
    if not queue:
        return

    # Remove all handlers and add the Queue handler as the only one.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    queue_handler = QueueHandler(queue)
    queue_handler.setLevel(logging.DEBUG)

    logger.addHandler(queue_handler)

    # Change current thread name for log record
    threading.current_thread().name = multiprocessing.current_process().name


def initLogger(console=False, log_dir=False, verbose=False):
    """
    Setup log It uses the logger instance with the name
    'MonitorMaster'. Three log handlers are added:
    * RotatingFileHandler: for the file monitormaster.log
    * LogListHandler: for Web UI
    * StreamHandler: for console (if console)
    Console log is only enabled if console is set to True. This method can
    be invoked multiple times, during different stages of MonitorMaster.
    """

    # Close and remove old handlers. This is required to reinit the loggers
    # at runtime
    for handler in logger.handlers[:]:
        # Just make sure it is cleaned up.
        if isinstance(handler, handlers.RotatingFileHandler):
            handler.close()
        elif isinstance(handler, logging.StreamHandler):
            handler.flush()

        logger.removeHandler(handler)

    # Configure the logger to accept all messages
    logger.propagate = False
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Add list logger
    loglist_handler = LogListHandler()
    loglist_handler.setLevel(logging.DEBUG)

    logger.addHandler(loglist_handler)

    # Setup file logger
    if log_dir:
        filename = os.path.join(log_dir, FILENAME)

        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s :: %(threadName)s :: %(message)s', '%Y%m%d-%H:%M:%S')
        file_handler = handlers.RotatingFileHandler(filename, maxBytes=MAX_SIZE,
                                                    backupCount=MAX_FILES)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)

    # Setup console logger
    if console:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s :: %(threadName)s :: %(message)s', '%Y%m%d-%H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)

        logger.addHandler(console_handler)

    # Install exception hooks
    initHooks()


def initHooks(global_exceptions=True, thread_exceptions=True, pass_original=True):
    """
    This method installs exception catching mechanisms. Any exception caught
    will pass through the exception hook, and will be logged to the logger as
    an error. Additionally, a traceback is provided.
    This is very useful for crashing threads and any other bugs, that may not
    be exposed when running as daemon.
    The default exception hook is still considered, if pass_original is True.
    """

    def excepthook(*exception_info):
        # We should always catch this to prevent loops!
        try:
            message = "".join(traceback.format_exception(*exception_info))
            logger.error("Uncaught exception: %s", message)
        except:
            pass

        # Original excepthook
        if pass_original:
            sys.__excepthook__(*exception_info)

    # Global exception hook
    if global_exceptions:
        sys.excepthook = excepthook

    # Thread exception hook
    if thread_exceptions:
        old_init = threading.Thread.__init__

        def new_init(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            old_run = self.run

            def new_run(*args, **kwargs):
                try:
                    old_run(*args, **kwargs)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    excepthook(*sys.exc_info())

            self.run = new_run

        # Monkey patch the run() by monkey patching the __init__ method
        threading.Thread.__init__ = new_init


# Expose logger methods
info = logger.info
warn = logger.warn
error = logger.error
debug = logger.debug
warning = logger.warning
exception = logger.exception
