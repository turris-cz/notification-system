import yaml
import logging


class Plugin:
    def __init__(self, name, actions, templates, notifications):
        self.name = name
        self.actions = []
        self.templates = []
        self.notification_types = {}

        self.init_logger()

        for a in actions:
            self.actions.append(a)

        for t in templates:
            self.templates.append(t)

        self.logger.debug("%s" % notifications)
        for n in notifications:
            self.logger.debug("concrete notif: %s" % n)
            self.notification_types[n['name']] = n

    def init_logger(self):
        self.logger = logging.getLogger("notifylib")

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            data = yaml.load(f)
            # TODO: better filename spliting handling
            name = filename.split('.')[0].split('/')[-1]

            # print("YML data {}".format(data))

            return cls(name, **data)

    def get_actions(self):
        return self.actions

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
