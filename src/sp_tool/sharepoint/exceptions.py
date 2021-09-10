"""
Exceptions for sharepoint api connector
"""


class BaseSharepointException(Exception):
    """ Base Sharepoint Exception """


class APICallFailedSharepointException(Exception):
    """ Base Sharepoint Exception """

    def __init__(self, code, err_msg):
        """ Initializer"""
        super().__init__(f"Error: {code}: {err_msg}")
        self.code = code
        self.err_msg = err_msg
