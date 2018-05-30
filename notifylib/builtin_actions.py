import logging

from .helpers import remove
from .config import config

logger = logging.getLogger(config["logging"]["logger_name"])


def dismiss(msg_id):
    """Dismiss message -> delete it"""
    logger.debug("Dismissing msg id {}".format(msg_id))
    remove(msg_id)


actions = {
    'dismiss': dismiss
}
