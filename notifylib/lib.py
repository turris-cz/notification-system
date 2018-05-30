import os
import json
import logging
import pprint

from datetime import datetime

from .helpers import generate_id, store, get_message_filename
from .builtin_actions import actions
from .config import config, load_config

# TODO: merge builtin actions with plugins action

logger = logging.getLogger(config["logging"]["logger_name"])


# TODO: Place the functions somewhere else in lib
# helpers?


def delete_messages():
    """Delete messages based on their timeout"""
    to_delete = []
    now = datetime.utcnow()

    for msg_dir in (config["dirs"]["volatile"], config["dirs"]["persistent"]):
        for filename in os.listdir(msg_dir):
            fh = get_message_filename(filename)

            with open(fh, 'r') as f:
                j_content = json.load(f)

                if "timeout" in j_content:
                    creat_time = datetime.fromtimestamp(float(j_content["id"]))
                    delta = now - creat_time

                    if delta.total_seconds() > int(j_content["timeout"]):
                        to_delete.append(j_content["id"])

    for file_id in to_delete:
        actions["dismiss"](file_id)


def delete_old_messages_before(func_to_decorate):
    """Decorator for delete_messages"""

    def wrapper(*args, **kwargs):
        delete_messages()

        return func_to_decorate(*args, **kwargs)

    return wrapper


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

    store(**kwargs)
    broadcast(msg_id)


@delete_old_messages_before
def list_all():
    """List all notifications"""
    out = []

    for msg_dir in (config["dirs"]["volatile"], config["dirs"]["persistent"]):
        for filename in os.listdir(msg_dir):
            fh = get_message_filename(filename)

            with open(fh, 'r') as f:
                content = f.read()
                out.append(content)

    return out


@delete_old_messages_before
def list(msg_id):
    """User command to list specific message"""
    filename = get_message_filename(msg_id)

    with open(filename, 'r') as f:
        content = f.read()

    return content

