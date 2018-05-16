import os
import subprocess
from datetime import datetime

import yaml

basedir = os.path.join(os.getcwd(), 'tmp')


def file_path(name):
    """Wrapper around os.path to simplify code"""
    return os.path.join(basedir, name)


def generate_id():
    """Unique id of message based on timestamp"""
    return datetime.utcnow().timestamp()


def store(text):
    """Store new message to local fs"""
    msg_id = generate_id()

    with open(file_path(str(msg_id)), 'w') as f:
        content = {'id': msg_id, 'text': text}

        yaml.dump(content, f, default_flow_style=False)


def remove(id):
    """Remove message identified by ID from local fs"""
    # TODO: try to check if msg exist upper in chain of function call
    msg_id = get_message(id)

    if msg_id:
        filename = file_path(msg_id)

        # TODO: refactor to atomic delete via mv
        subprocess.call(["rm", filename])


def get_message(id):
    """Get specific message from local fs"""
    for filename in os.listdir(basedir):
        if filename == id:
            return filename
