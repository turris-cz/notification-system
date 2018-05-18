import logging
import configparser
import os

from .helpers import remove

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(os.path.join(BASE_PATH, "config.conf"))

logger = logging.getLogger(config["logging"]["logger_name"])


def dismiss(id):
    """Dismiss message -> delete it"""
    logger.debug("Dismissing msg id {}".format(id))
    remove(id)
