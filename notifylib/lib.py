import os
import yaml
import logging

from .helpers import store, get_message_filename
from .builtin_actions import dismiss
from .config import config, load_config

# TODO: maybe some import from builtins?
# TODO: merge builtins with plugins at startup
actions = {
    'dismiss': dismiss
}

logger = logging.getLogger(config["logging"]["logger_name"])


def set_config(filename):
    """
    Load config supplied by user
    Usefull for developement
    """
    load_config(filename)


def load_plugins():
    pass


def broadcast(msg):
    """Broadcast message via msgbus"""
    pass


def connect_to_bus():
    """Connect to msgbus"""
    pass


def call(action, **kwargs):
    """Call defined action with or without optional kwargs"""
    try:
        actions[action](**kwargs)
    except KeyError:
        logger.warning("Unrecognized action '{:s}'".format(action))


def add(text, **kwargs):
    """Store and broadcast new notification"""
    logger.debug("Storing new notification {}".format(text))
    store(text, **kwargs)
    broadcast(text)


def list_all():
    """List all notifications"""
    for dir in (config["dirs"]["volatile"], config["dirs"]["persistent"]):
        for filename in os.listdir(dir):
            fh = get_message_filename(filename)

            with open(fh, 'r') as f:
                content = f.readlines()
                print(content)


def list(id):
    """User command to list specific message"""
    filename = get_message_filename(id)

    with open(filename, 'r') as f:
        content = yaml.load(f)

    print(content)
