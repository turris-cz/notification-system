import os
import yaml

from .helpers import store, get_message, basedir, file_path
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
        if kwargs:
            actions[action](**kwargs)
        else:
            actions[action]()
    except KeyError:
        print("Action not found...")


def add(text):
    """Store and broadcast new notification"""
    print("Storing new notification {}".format(text))
    store(text)
    broadcast(text)


def list_all():
    """List all notifications"""
    for filename in os.listdir(basedir):
        with open(file_path(filename), 'r') as f:
            content = f.readlines()
            print(content)


def list(id):
    """User command to list specific message"""
    filename = get_message(id)

    with open(file_path(filename), 'r') as f:
        content = yaml.load(f)

    print(content)
