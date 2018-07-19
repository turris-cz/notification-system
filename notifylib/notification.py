import json


class Notification:
    def __init__(self, timestamp, skeleton, persistent=False, **opts):
        self.notif_id = timestamp
        self.timestamp = timestamp
        self.skeleton = skeleton
        self.opts = opts
        self.persistent = persistent

        # TODO: parse opts into metadata
        self.content = opts['message']

    @classmethod
    def from_file(cls, f):
        """Load notification from it's file"""
        try:
            dict = json.load(f)
            return cls(**dict)
        except Exception:
            pass
            # TODO: log failure

    def valid(self, timestamp):
        """If notification is still valid"""
        pass

    def render(self):
        """Return rendered template as text"""
        pass

    def serialize_metadata(self):
        """Return serialized data as json"""
        return "Content:{}".format(self.content)

    def __str__(self):
        out = "{\n"
        out += "\tbase_type: {}\n".format(self.skeleton)
        out += "\ttimestamp: {}\n".format(self.timestamp)
        out += "}\n"

        return out
