import json


class NotificationSkeleton:
    def __init__(self, name, template, actions):
        self.name = name
        self.template = template
        self.actions = actions

    def serialize(self):
        json_data = {
            'name': self.name,
            'template': self.template,
            'actions': self.actions,
        }

        return json.dumps(json_data)

    def __str__(self):
        out = "{\n"
        out += "\tname: {}\n".format(self.name)
        out += "\ttemplate: {}\n".format(self.template)
        out += "\tactions: {}\n".format(self.actions)
        out += "}\n"

        return out
