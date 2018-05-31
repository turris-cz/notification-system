import os
import subprocess
import yaml
import json
import logging

from datetime import datetime

from .config import config

logger = logging.getLogger("notifylib")


def basedir(persistent=False):
    """Return basedir by msg persistence"""
    if persistent:
        return config.get("settings", "persistent_dir")
    else:
        return config.get("settings", "volatile_dir")


def file_path(name, persistent=False):
    """Wrapper around os.path to simplify code"""
    return os.path.join(basedir(persistent), name)


def persistent_file_path(name):
    return file_path(name, persistent=True)


def volatile_file_path(name):
    return file_path(name)


def generate_id():
    """Unique id of message based on timestamp"""
    return datetime.utcnow().timestamp()


def store(**kwargs):
    """Store new message to local fs"""
    msg_id = str(kwargs['id'])
    persistent = False

    if kwargs["persistent"]:
        filename = persistent_file_path(msg_id)
        persistent = True
    else:
        filename = volatile_file_path(msg_id)

    with open(filename, 'w') as f:
        # very simple content...
        content = {
            'id': msg_id,
            'text': kwargs['message'],
            'action': kwargs['action'],
            'severity': kwargs['severity']
        }

        if persistent:
            content["persistent"] = True

        if kwargs['timeout']:
            content['timeout'] = kwargs['timeout']

        json.dump(content, f)


def remove(msg_id):
    """Remove message identified by ID from local fs"""
    # TODO: try to check if msg exist upper in chain of function call
    filename = get_message_filename(msg_id)

    if filename:
        # TODO: refactor to atomic delete via mv
        subprocess.call(["rm", filename])


def get_message_filename(msg_id):
    """Get full path to file on local fs based on msg id"""
    for filename in os.listdir(config.get("settings", "volatile_dir")):
        if filename == msg_id:
            return volatile_file_path(filename)

    for filename in os.listdir(config.get("settings", "persistent_dir")):
        if filename == msg_id:
            return persistent_file_path(filename)
