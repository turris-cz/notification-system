import json
import random

from datetime import datetime as dt

from jinja2 import TemplateSyntaxError, TemplateRuntimeError, TemplateAssertionError

from .logger import logger
from .notificationskeleton import NotificationSkeleton


class Notification:
    ATTRS = ['notif_id', 'timestamp', 'persistent', 'timeout', 'message', 'fallback']

    def __init__(self, notif_id, timestamp, skeleton, fallback=None, persistent=False, timeout=None, **data):
        self.notif_id = notif_id
        self.timestamp = timestamp

        self.skeleton = skeleton

        self.data = data
        self.persistent = persistent
        self.timeout = timeout
        self.fallback = fallback

        # TODO: parse opts into metadata
        self.message = self.data['message']

        if not self.fallback:
            self.fallback = self.render_all()

    @classmethod
    def new(cls, skel, **data):
        """Generate some mandatory params during creation"""
        nid = cls._generate_id()
        ts = cls._generate_timestamp()

        n = cls(nid, ts, skel, **data)

        return n

    @classmethod
    def from_file(cls, path):
        """Load notification from it's file"""
        try:
            with open(path, 'r') as f:
                json_data = json.load(f)

            skel_obj = NotificationSkeleton(**json_data['skeleton'])
            json_data['skeleton'] = skel_obj  # replace json data with skeleton instance

            return cls(**json_data)

        # TODO: exception handling
        except Exception as e:
            # TODO: proper logging per exception
            logger.warning("Failed to deserialize json file: %s", e)

    def valid(self, timestamp=None):
        """If notification is still valid"""
        if self.timeout:
            if not timestamp:
                timestamp = Notification._generate_timestamp()

            creat_time = dt.fromtimestamp(self.timestamp)
            delta = timestamp - creat_time

            return delta.total_seconds() < self.timeout

        return True

    def render(self, media_type, lang):
        """Return rendered template as given media type and in given language"""
        try:
            return self.skeleton.render(media_type, lang, self.message)
        except (TemplateSyntaxError, TemplateRuntimeError, TemplateAssertionError) as e:
            print("exception caught: {}".format(e))
            return self.fallback

    def render_all(self):
        """Render all media types in default languages"""
        ret = {}
        # default_langs = ['en', 'cz']

        for mt in self.skeleton.get_media_types():
            # render in default lang -> en
            ret[mt] = self.render(mt, 'en')

            # for lang in default_langs:
            #     ret[mt] = self.render(mt, lang)

        return ret

    def serialize(self):
        """Return serialized data"""
        json_data = {}

        for attr in self.ATTRS:
            json_data[attr] = getattr(self, attr)

        json_data['skeleton'] = self.skeleton.serialize()

        return json.dumps(json_data)

    @classmethod
    def _generate_id(cls):
        """
        Generate unique id of message based on timestamp

        returned as string
        """
        ts = int(cls._generate_timestamp())  # rounding to int
        # append random number for uniqueness
        unique = random.randint(1, 1000)

        return "{}-{}".format(ts, unique)

    @classmethod
    def _generate_timestamp(cls):
        """Create UTC timestamp"""
        return dt.utcnow().timestamp()

    def __str__(self):
        out = "{\n"
        out += "\tnotif_id: {}\n".format(self.notif_id)
        out += "\tskeleton: {}\n".format(self.skeleton)
        out += "\ttimestamp: {}\n".format(self.timestamp)
        out += "\tpersistent: {}\n".format(self.persistent)
        out += "\ttimeout: {}\n".format(self.timeout)
        out += "\tmessage: {}\n".format(self.message)
        out += "}\n"

        return out
