"""
Mock Logger for testing
"""
import logging


class MockLogger:
    """ Mock Logger"""

    def __init__(self):
        """ Initialize"""
        self.messages = []
        self.last_level = None
        self.last_msg = None

    def reset(self):
        """ Reset to defaults"""
        self.messages = []
        self.last_level = None
        self.last_msg = None

    def log(self, level, msg, *params):
        """ Log a message """
        self.last_level = level
        message = msg % params
        self.last_msg = message
        self.messages.append((level, message, msg, params))

    def debug(self, msg, *params):
        """ Log a debug message """
        self.log(logging.DEBUG, msg, *params)

    def info(self, msg, *params):
        """ Log an info message"""
        self.log(logging.INFO, msg, *params)

    @property
    def last_message(self):
        """ Get last formatted message as a level, message tuple """
        if not self.messages:
            return (None, None)
        return self.messages[-1][0:2]

    @property
    def last_message_raw(self):
        """
            Get last unformatted message as aevel, formatstring, params tuple
        """
        if not self.messages:
            return None, None, []
        return self.messages[-1][0], self.messages[-1][2], self.messages[-1][3]
