import os
import json
import yaml
import logging
import pprint
from collections import namedtuple

from datetime import datetime

from .helpers import generate_id, store, get_message_filename
from .builtin_actions import actions
# from .template import Template
from .config import config, load_config

# TODO: merge builtin actions with plugins action

logger = logging.getLogger("notifylib")

# named tumples
Action = namedtuple('Action', 'name title command')
Notification = namedtuple('Notification', 'name template actions')
Template = namedtuple('Template', 'type media src')

# plugin_actions = {}
templates = {}
notifications = {}

# TODO: Place the functions somewhere else in lib
# helpers?


def delete_messages():
    """Delete messages based on their timeout"""
    to_delete = []
    now = datetime.utcnow()

    for msg_dir in (config.get("settings", "volatile_dir"), config.get("settings", "persistent_dir")):
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


def action_wrapper(a):
    """Parse action for executable command and return it as callable"""
    def wrapped():
        # do something usefull with action cmd
        print("Executing cmd = {}".format(a.command))

    return wrapped


def set_config(filename):
    """
    Load config supplied by user
    Usefull for developement
    """
    load_config(filename)


def load_plugins():
    plugin_dir = config.get("settings", "plugin_dir")

    for plugin in os.listdir(plugin_dir):
        if plugin.startswith('.'):  # filter out dot files
            continue

        with open(os.path.join(plugin_dir, plugin), "r") as f:
            try:
                yml_content = yaml.safe_load(f)

                yml_actions = yml_content['actions']
                for a in yml_actions:
                    name = a['name']
                    title = a['title']
                    command = a['command']

                    acc = Action(name=name, title=title, command=command)

                    actions[name] = action_wrapper(acc)

                yml_templates = yml_content['templates']
                for t in yml_templates:
                    type = t['type']
                    media = t['supported_media']
                    src = t['src']

                    tpl = Template(type, media, src)

                    templates[type] = tpl

                yml_notifications = yml_content['notifications']
                for n in yml_notifications:
                    name = n['name']
                    template = n['template']
                    n_actions = n['actions']

                    notification = Notification(name, templates[template], n_actions)

                    notifications[name] = notification

            except yaml.YAMLError as exc:
                print(exc)


def print_plugins():
    for k, v in templates.items():
        logger.debug("{} = {}".format(k, v))

    for k, v in actions.items():
        logger.debug("{} = {}".format(k, v))

    for k, v in notifications.items():
        logger.debug("{} = {}".format(k, v))


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

    for msg_dir in (config.get("settings", "volatile_dir"), config.get("settings", "persistent_dir")):
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
