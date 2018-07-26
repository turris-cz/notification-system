import json
import random

from datetime import datetime as dt

from jinja2 import TemplateSyntaxError, TemplateRuntimeError, TemplateAssertionError

from .logger import logger
from .notificationskeleton import NotificationSkeleton


class Notification:
    def __init__(self, notif_id, timestamp, skeleton, fallback=None, persistent=False, **data):
        self.notif_id = notif_id
        self.timestamp = timestamp

        self.skeleton = skeleton

        self.data = data
        self.persistent = persistent
        self.fallback = fallback

        # TODO: parse opts into metadata
        self.content = self.data['message']

        if not self.fallback:
            self.fallback = self.render_all()

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
                json_data = json.load(f)

            skel_obj = NotificationSkeleton(**json_data['skeleton'])
            json_data['skeleton'] = skel_obj  # replace json data with skeleton instance

            return cls(**json_data)

        # TODO: exception handling
        except Exception as e:
            # TODO: proper logging per exception
            logger.warn("Failed to deserialize json file: %s" % e)

    def valid(self, timestamp=None):
        """If notification is still valid"""
        if not timestamp:
            ts = Notification.generate_timestamp()

        # TODO: compare self.timestamp an ts

    def render(self, media_type, lang):
        """Return rendered template as given media type and in given language"""
        try:
            return self.skeleton.render(media_type, lang, self.content)
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
        json_data = {
            'notif_id': self.notif_id,
            'timestamp': self.timestamp,
            'persistent': self.persistent,
            'message': self.content,
            'skeleton': self.skeleton.serialize(),
            'fallback': self.fallback,
        }

        return json.dumps(json_data)

    @classmethod
    def generate_id(cls):
        """
        Unique id of message based on timestamp
        returned as string
        """
        ts = int(cls.generate_timestamp())  # rounding to int
        # append random number for uniqueness
        unique = random.randint(1, 1000)

        return "{}-{}".format(ts, unique)

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
