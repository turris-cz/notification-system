import os
import yaml
import logging

from .helpers import generate_id, store, get_message_filename
from .builtin_actions import actions
from .config import config, load_config

# TODO: merge builtin actions with plugins action

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


def add(**kwargs):
    """
    Store and broadcast new notification
    TODO: use fixed set of keyword params instead of kwargs
    """
    msg_id = generate_id()

    logger.debug("Storing new notification {}".format(msg_id))

    kwargs['id'] = msg_id

    store(**kwargs)
    broadcast(msg_id)


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
