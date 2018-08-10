import json
import random

from datetime import datetime
from jinja2 import TemplateError

from .exceptions import CreateNotificationError, NotificationTemplatingError
from .logger import logger
from .notificationskeleton import NotificationSkeleton


class Notification:
    ATTRS = ['notif_id', 'timestamp', 'skeleton', 'persistent', 'timeout', 'data', 'fallback']

    def __init__(self, notif_id, timestamp, skeleton, data, fallback=None, persistent=False, timeout=None):
        self.notif_id = notif_id
        self.timestamp = timestamp

        self.skeleton = skeleton

        self.persistent = persistent
        self.timeout = timeout
        self.fallback = fallback

        self.data = data

        if not self.fallback:
            self.fallback = self.render_fallback_data()

    @classmethod
    def new(cls, skel, **opts):
        """Generate some mandatory params during creation"""
        nid = cls._generate_id()
        ts = int(datetime.utcnow().timestamp())

        n = cls(nid, ts, skel, **opts)

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
                timestamp = int(datetime.utcnow().timestamp())

            creat_time = datetime.fromtimestamp(self.timestamp)
            delta = timestamp - creat_time

            return delta.total_seconds() < self.timeout

        return True

    def render_template(self, media_type, lang):
        try:
            return self.skeleton.render(media_type, lang, self.data)
        except TemplateError:
            raise NotificationTemplatingError("Failed to render template")

    def render(self, media_type, lang):
        """Return rendered template as given media type and in given language"""
        try:
            return self.render_template(media_type, lang)
        except NotificationTemplatingError:
            return self.fallback[media_type]

    def render_fallback_data(self):
        """Render all media types in default languages"""
        ret = {}
        try:

            for mt in self.skeleton.get_media_types():
                # render in default lang -> en
                ret[mt] = self.render_template(mt, 'en')

        except NotificationTemplatingError as e:
            raise CreateNotificationError("Couldn't create notification with given template variables")

        return ret

    def serialize(self):
        """Return serialized data"""
        json_data = {}

        for attr in self.ATTRS:
            data = getattr(self, attr)
            if hasattr(data, 'serialize'):
                data = data.serialize()

            json_data[attr] = data

        return json.dumps(json_data, indent=4)

    @staticmethod
    def _generate_id():
        """
        Generate unique id of message based on timestamp

        returned as string
        """
        ts = int(datetime.utcnow().timestamp())
        rand = random.randint(1, 1000)

        # append random number for uniqueness
        return "{}-{}".format(ts, rand)

    def __str__(self):
        # TODO: print using getattr?
        out = "{\n"
        out += "\tnotif_id: {}\n".format(self.notif_id)
        out += "\tskeleton: {}\n".format(self.skeleton)
        out += "\ttimestamp: {}\n".format(self.timestamp)
        out += "\tpersistent: {}\n".format(self.persistent)
        out += "\ttimeout: {}\n".format(self.timeout)
        out += "\tjinja_vars: {}\n".format(self.jinja_vars)
        out += "}\n"

        return out
