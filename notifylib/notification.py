import json
import logging
# TODO: global logging

from datetime import datetime as dt

from .notificationskeleton import NotificationSkeleton


class Notification:
    def __init__(self, notif_id, timestamp, skeleton, persistent=False, **data):
        self.notif_id = notif_id
        self.timestamp = timestamp

        self.skeleton = skeleton

        self.data = data
        self.persistent = persistent

        self.init_logger()

        # TODO: parse opts into metadata
        self.content = self.data['message']

    @classmethod
    def new(cls, skel, **data):
        """Generate some mandatory params during creation"""
        nid = cls.generate_id()
        ts = cls.generate_timestamp()

        n = cls(nid, ts, skel, **data)

        return n

    @classmethod
    def from_file(cls, path):
        """Load notification from it's file"""
        try:
            with open(path, 'r') as f:
                dict = json.load(f)

            j_skel = dict['skeleton']

            skel_obj = NotificationSkeleton(j_skel['name'], j_skel['template'], j_skel['actions'])
            dict['skeleton'] = skel_obj  # replace json data with skeleton object

            n = cls(**dict)

            # set attributes of this instance
            # if 'persistent' in dict:
            #     n.persistent = True

            return n
        except Exception as e:
            # TODO: proper logging
            print("Failed to deserialize json file; Error: {}".format(e))

    def init_logger(self):
        self.logger = logging.getLogger("notifylib")

    def valid(self, timestamp=None):
        """If notification is still valid"""
        if not timestamp:
            t = Notification.generate_timestamp()

        # TODO: compare self.timestamp an t

    def render(self):
        """Return rendered template as text"""
        pass

    def serialize(self):
        """Return serialized data"""
        json_data = {
            'notif_id': self.notif_id,
            'timestamp': self.timestamp,
            'persistent': self.persistent,
            'message': self.content,
            'skeleton': self.skeleton.serialize(),
        }

        return json.dumps(json_data)

    @classmethod
    def generate_id(cls):
        """Unique id of message based on timestamp"""
        return cls.generate_timestamp()
        # TODO: append random number for uniqueness

    @classmethod
    def generate_timestamp(cls):
        """Create UTC timestamp"""
        return dt.utcnow().timestamp()

    def __str__(self):
        out = "{\n"
        out += "\tnotif_id: {}\n".format(self.notif_id)
        out += "\tskeleton: {}\n".format(self.skeleton)
        out += "\ttimestamp: {}\n".format(self.timestamp)
        out += "\tpersistent: {}\n".format(self.persistent)
        out += "\tmessage: {}\n".format(self.content)
        out += "}\n"

        return out
