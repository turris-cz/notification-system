import os
import subprocess
from datetime import datetime

import yaml

basedir = os.path.join(os.getcwd(), 'tmp')


def generate_id():
    """Unique id of message based on timestamp"""
    return datetime.utcnow().timestamp()


def store(text):
    """Store new message to local fs"""
    msg_id = generate_id()
    newfilename = "{}.yml".format(msg_id)

    with open(os.path.join(basedir, newfilename), 'w') as f:
        content = {'id': msg_id, 'text': text}

        yaml.dump(content, f, default_flow_style=False)


def remove(id):
    """Remove message identified by ID from local fs"""
    filename = os.path.join(basedir, get_message(id))

    # TODO: refactor to atomic delete via mv
    subprocess.call(["rm", filename])


def get_message(id):
    """Get specific message from local fs"""
    for filename in os.listdir(basedir):
        if filename == "{}.yml".format(id):
            return filename
