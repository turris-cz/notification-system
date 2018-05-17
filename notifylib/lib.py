import os
import yaml

from .helpers import store, volatile_basedir, persistent_basedir, get_message_filename
from .builtin_actions import dismiss, reboot

actions = {
    'reboot': reboot,
    'dismiss': dismiss
}


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
        print("Action not found...")


def add(text, **kwargs):
    """Store and broadcast new notification"""
    print("Storing new notification {}".format(text))
    store(text, **kwargs)
    broadcast(text)


def list_all():
    """List all notifications"""
    for dir in (volatile_basedir, persistent_basedir):
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
