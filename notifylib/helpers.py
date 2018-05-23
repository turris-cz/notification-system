import os
import subprocess
import yaml
import logging

from datetime import datetime

from .config import config

logger = logging.getLogger(config["logging"]["logger_name"])


def basedir(persistent=False):
    """Return basedir by msg persistence"""
    if persistent:
        return config["dirs"]["persistent"]
    else:
        return config["dirs"]["volatile"]


def file_path(name, persistent=False):
    """Wrapper around os.path to simplify code"""
    return os.path.join(basedir(persistent), name)


def generate_id():
    """Unique id of message based on timestamp"""
    return datetime.utcnow().timestamp()


def store(text, **kwargs):
    """Store new message to local fs"""
    msg_id = generate_id()
    persistent = False

    if kwargs:
        if kwargs["persistent"]:
            filename = file_path(str(msg_id), persistent=True)
            persistent = True
    else:
        filename = file_path(str(msg_id))

    with open(filename, 'w') as f:
        # very simple content...
        content = {'id': msg_id, 'text': text}

        if (persistent):
            content["persistent"] = True

        yaml.dump(content, f, default_flow_style=False)


def remove(id):
    """Remove message identified by ID from local fs"""
    # TODO: try to check if msg exist upper in chain of function call
    filename = get_message_filename(id)

    if filename:
        # TODO: refactor to atomic delete via mv
        subprocess.call(["rm", filename])


def get_message_filename(id):
    """Get full path to file on local fs based on msg id"""
    for filename in os.listdir(config["dirs"]["volatile"]):
        if filename == id:
            return file_path(filename)

    for filename in os.listdir(config["dirs"]["persistent"]):
        if filename == id:
            return file_path(filename, persistent=True)
