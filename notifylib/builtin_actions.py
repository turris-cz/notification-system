import logging

from .helpers import remove

logger = logging.getLogger("notifylib")


def dismiss(id):
    """Dismiss message -> delete it"""
    logger.debug("Dismissing msg id {}".format(id))
    remove(id)
