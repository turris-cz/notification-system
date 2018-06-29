import logging

from .helpers import generate_id, store
from .builtin_actions import actions
# from .template import Template
from .config import load_config
from .datalayer import datalayer

logger = logging.getLogger("notifylib")


def delete_old_messages_before(func_to_decorate):
    """Decorator for delete_messages"""

    def wrapper(*args, **kwargs):
        datalayer.delete_messages()

        return func_to_decorate(*args, **kwargs)

    return wrapper


def set_config(filename):
    """
    Load config supplied by user
    Usefull for developement
    """
    load_config(filename)


def load_plugins():
    datalayer.load_plugins()


def print_plugins():
    datalayer.print_plugins()


def broadcast(msg):
    """Broadcast message via msgbus"""
    pass


def connect_to_bus():
    """Connect to msgbus"""
    pass


@delete_old_messages_before
def call(action, **kwargs):
    """Call defined action with or without optional kwargs"""
    if action in actions:
        actions[action](**kwargs)
    else:
        logger.warning("Unrecognized action '{:s}'".format(action))


@delete_old_messages_before
def add(**kwargs):
    """
    Store and broadcast new notification
    TODO: use fixed set of keyword params instead of kwargs
    """
    msg_id = generate_id()

    logger.debug("Storing new notification {}".format(msg_id))

    kwargs['id'] = msg_id

    # TODO: datalayer.store(**kwargs)
    store(**kwargs)
    broadcast(msg_id)


@delete_old_messages_before
def list_all():
    """List all notifications"""
    return datalayer.list_all()


@delete_old_messages_before
def list(msg_id):
    """User command to list specific message"""
    return datalayer.list(msg_id)
