import json
import random
import shlex
import subprocess

from datetime import datetime
from jinja2 import TemplateError
from types import SimpleNamespace

from .exceptions import CreateNotificationError, NotificationTemplatingError
from .logger import logger
from .notificationskeleton import NotificationSkeleton


class Notification:
    ATTRS = ['notif_id', 'timestamp', 'skeleton', 'persistent', 'timeout', 'severity', 'data', 'fallback', 'valid']

    def __init__(self, notif_id, timestamp, skeleton, data, persistent, timeout, severity, fallback=None, valid=True):
        self.notif_id = notif_id
        self.timestamp = timestamp

        self.skeleton = skeleton

        self.fallback = fallback
        self.persistent = persistent
        self.timeout = timeout
        self.severity = severity

        self.valid = valid

        self.data = data

        if not self.fallback:
            self.fallback = self.render_fallback_data()

    @classmethod
    def new(cls, skel, **opts):
        """Generate mandatory params during creation and return new instance"""
        nid = cls._generate_id()
        ts = int(datetime.utcnow().timestamp())

        n = cls(nid, ts, skel, **opts)

        return n

    @classmethod
    def from_file(cls, path):
        """Load notification from it's file and return new instance"""
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

    def is_valid(self, timestamp=None):
        """If notification is still valid based on multiple conditions"""
        if not timestamp:
            timestamp = int(datetime.utcnow().timestamp())

        if not self.valid:
            return False

        if self.timeout:
            create_time = datetime.fromtimestamp(self.timestamp)
            delta = timestamp - create_time

            if delta.total_seconds() >= self.timeout:
                return False

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

    def _serialize_data(self):
        """Return serialized attributes of instance in dictionary"""
        attrs = {}

        for attr in self.ATTRS:
            data = getattr(self, attr)
            if hasattr(data, 'serialize'):
                data = data.serialize()

            attrs[attr] = data

        return attrs

    def serialize(self):
        """Return serialized data as json"""
        return json.dumps(self._serialize_data(), indent=4)

    def get_data(self):
        """Return instance content as SimpleNamespace"""
        return SimpleNamespace(**self._serialize_data())

    def dismiss(self):
        self.valid = False

    def call_action(self, name, dry_run=True):
        action_cmd = self.skeleton.get_action(name)

        if not action_cmd:
            logger.debug("Action '%s' not available", name)
            return

        if dry_run:
            print("Dry run: executing command '{}'".format(action_cmd))
        else:
            # TODO: validate command string somehow
            cmd = shlex.split(action_cmd)
            res = subprocess.run(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

            if res.returncode != 0:
                # TODO: create notification with this info
                print("Command failed with exit code {}".format(res.returncode))
                print("stdout: {}".format(res.stdout))
                print("stderr: {}".format(res.stderr))
            else:
                print("Command exited succesfully")

    @staticmethod
    def _generate_id():
        """
        Generate unique id of message based on timestamp

        returned as string
        """
        ts = int(datetime.utcnow().timestamp())
        rand = random.randint(10000, 99999)

        # add random number for uniqueness
        return "{}-{}".format(rand, ts)

    def __str__(self):
        out = "{\n"

        for attr in self.ATTRS:
            data = getattr(self, attr)
            if hasattr(data, 'serialize'):
                data = data.serialize()

            out += "\t{}: {}\n".format(attr, data)

        out += "}\n"

        return out
