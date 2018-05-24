import logging

from .helpers import remove
from .config import config

logger = logging.getLogger(config["logging"]["logger_name"])


def dismiss(id):
    """Dismiss message -> delete it"""
    logger.debug("Dismissing msg id {}".format(id))
    remove(id)


actions = {
    'dismiss': dismiss
}
