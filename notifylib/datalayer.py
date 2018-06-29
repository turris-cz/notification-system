import yaml
import json
import logging
import os
import datetime
from collections import namedtuple

from .actions import actions
from .config import config
from .helpers import generate_id, get_message_filename

logger = logging.getLogger("notifylib")

# named tumples
Action = namedtuple('Action', 'name title command')
Notification = namedtuple('Notification', 'name template actions')
Template = namedtuple('Template', 'type media src')


class Datalayer:
    def __init__(self):
        self.templates = {}
        self.notifications = {}

    def action_wrapper(self, a):
        """Parse action for executable command and return it as callable"""
        def wrapped():
            # do something usefull with action cmd
            print("Executing cmd = {}".format(a.command))

        return wrapped

    # TODO: merge builtin actions with plugins action somewhere
    def load_plugins(self):
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

                        actions[name] = self.action_wrapper(acc)

                    yml_templates = yml_content['templates']
                    for t in yml_templates:
                        type = t['type']
                        media = t['supported_media']
                        src = t['src']

                        tpl = Template(type, media, src)

                        self.templates[type] = tpl

                    yml_notifications = yml_content['notifications']
                    for n in yml_notifications:
                        name = n['name']
                        template = n['template']
                        n_actions = n['actions']

                        notification = Notification(name, self.templates[template], n_actions)

                        self.notifications[name] = notification

                except yaml.YAMLError as exc:
                    print(exc)

    def print_plugins(self):
        for k, v in self.templates.items():
            logger.debug("{} = {}".format(k, v))

        for k, v in actions.items():
            logger.debug("{} = {}".format(k, v))

        for k, v in self.otifications.items():
            logger.debug("{} = {}".format(k, v))

    def list_all(self):
        out = []

        for msg_dir in (config.get("settings", "volatile_dir"), config.get("settings", "persistent_dir")):
            for filename in os.listdir(msg_dir):
                fh = get_message_filename(filename)

                with open(fh, 'r') as f:
                    content = f.read()
                    out.append(content)

        return out

    def list(self, msg_id):
        filename = get_message_filename(msg_id)

        with open(filename, 'r') as f:
            content = f.read()

        return content

    def delete_messages(self):
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


datalayer = Datalayer()
