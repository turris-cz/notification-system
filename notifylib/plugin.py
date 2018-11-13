import pathlib
import yaml

from .logger import logger


class Plugin:
    def __init__(self, name, actions, templates, notifications):
        self.name = name
        self.actions = {}
        self.templates = {}
        self.notification_types = {}

        for a in actions:
            self.actions[a['name']] = a

        for t in templates:
            self.templates[t['type']] = t

        logger.debug("%s", notifications)
        for n in notifications:
            logger.debug("concrete notif: %s", n)
            self.notification_types[n['name']] = n

    @classmethod
    def from_file(cls, filepath):
        try:
            with open(filepath, 'r') as f:
                data = yaml.load(f)
        except FileNotFoundError:
            logger.warning("Failed to open plugin file '%s'", filepath)
            return None
        except yaml.YAMLError:
            logger.warning("Failed to deserialize yaml file '%s'", filepath)
            return None

        # Get only file name without suffix
        filename = pathlib.Path(filepath).stem

        return cls(filename, **data)

    def get_actions(self):
        return self.actions

    def get_templates(self):
        return self.templates

    def get_notification_types(self):
        return self.notification_types

    def __str__(self):
        """For debug purposes"""
        out = "{\n"
        out += "\tname: {}\n".format(self.name)
        for a in self.actions:
            out += "\tActions: {}\n".format(a)

        for t in self.templates:
            out += "\tTemplates: {}\n".format(t)

        for name, data in self.notification_types.items():
            out += "\tNotifications: {} : {}\n".format(name, data)

        out += "}"

        return out
