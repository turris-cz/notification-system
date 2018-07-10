import json


class Notification:
    def __init__(self, name, template, actions, timestamp=None, **opts):
        self.name = name
        self.template = template
        self.actions = actions

        self.timestamp = timestamp
        self.opts = opts

        # TODO: parse opts into metadata

    @classmethod
    def from_file(cls, f):
        """Load notification from it's file"""
        try:
            dict = json.load(f)
            return cls(**dict)
        except Exception:
            pass
            # TODO: log failure

    @classmethod
    def create_instance(cls, **args):
        return cls(args)

    def valid(self, timestamp):
        """If notification is still valid"""
        pass

    def __str__(self):
        pass
