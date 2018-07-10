import yaml


class Plugin:
    def __init__(self, name, actions, templates, notifications):
        self.name = name
        self.actions = []
        self.templates = []
        self.notifications = []

        for a in actions:
            self.actions.append(a)

        for t in templates:
            self.templates.append(t)

        for n in notifications:
            self.notifications.append(n)

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            data = yaml.load(f)
            # TODO: better filename spliting handling
            name = filename.split('.')[0].split('/')[1]

            # print("YML data {}".format(data))

            return cls(name, **data)

    def get_actions(self):
        return self.actions

    def get_notification_types(self):
        nt = []

        for n in self.notifications:
            nt.append(n)

        return nt

    def __str__(self):
        """For debug purposes"""
        out = "{\n"
        out += "\tname: {}\n".format(self.name)
        for a in self.actions:
            out += "\tActions: {}\n".format(a)

        for t in self.templates:
            out += "\tTemplates: {}\n".format(t)

        for n in self.notifications:
            out += "\tNotifications: {}\n".format(n)

        out += "}"

        return out
