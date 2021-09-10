""" Simple shared logging """
import logging

NAME = 'sp-tool'
LOG_FORMAT = "%(name)s:%(levelname).1s:%(message)s"

LOG = logging.getLogger(NAME)
LOG.setLevel(logging.INFO)


def initialize_logging(level=logging.INFO, format=LOG_FORMAT, **kwargs):
    """ Initialize logging (should only be done by cli """
    # pylint: disable=W0622
    logging.basicConfig(level=level, format=format, **kwargs)
