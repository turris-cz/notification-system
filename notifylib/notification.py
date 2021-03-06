import json
import logging
import uuid

from datetime import datetime
from jinja2 import TemplateError
from types import SimpleNamespace

from .config import config
from .exceptions import (
    CreateNotificationError,
    NoSuchTemplateError,
    NotificationTemplatingError,
    VersionMismatchError
)
from .notificationskeleton import NotificationSkeleton
from .supervisor import Supervisor

logger = logging.getLogger(__name__)


class Notification:
    ATTRS = ['notif_id', 'api_version', 'timestamp', 'skeleton', 'persistent', 'timeout', 'severity', 'data', 'fallback', 'valid', 'explicit_dismiss', 'default_action']
    # TODO: better name?
    META_ATTRS = ['persistent', 'timestamp', 'severity', 'default_action']
    API_VERSION = 1

    def __init__(self, notif_id, api_version, timestamp, skeleton, data, persistent, timeout, severity, fallback=None, valid=True, explicit_dismiss=True, default_action='dismiss'):
        self.notif_id = notif_id
        self.api_version = api_version
        self.timestamp = timestamp

        self.skeleton = skeleton

        self.fallback = fallback
        self.persistent = persistent
        self.timeout = timeout
        self.severity = severity
        self.explicit_dismiss = explicit_dismiss

        # default "closing" action
        # users will probably want to use "default" as simplest method to "just dismiss" notification
        if default_action in self.skeleton.actions:
            self.default_action = default_action
        else:
            self.default_action = 'dismiss'

        self.valid = valid

        self.data = data

        if not self.fallback:
            self.fallback = self.render_fallback_data()

    @classmethod
    def new(cls, skel, **opts):
        """Generate mandatory params during creation and return new instance"""
        nid = cls._generate_id()
        ts = int(datetime.utcnow().timestamp())

        n = cls(nid, cls.API_VERSION, ts, skel, **opts)

        return n

    @classmethod
    def from_file(cls, path, plugin_storage):
        """
        Load notification from it's file and return new instance

        If there is failure to open/deserialize i.e. get file, return None
        If there is invalid content, raise exception
        """
        try:
            with open(path, 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            logger.warning("Failed to open notification file '%s'", path)
            return None
        except json.JSONDecodeError as e:
            logger.warning("Failed to deserialize json file: %s", e)
            return None

        # Very simple validation based on API version
        if not cls.validate_version(json_data):
            raise VersionMismatchError

        skel_args = json_data['skeleton']
        plug = plugin_storage.get_plugin(skel_args['plugin_name'])

        if not plug:
            logger.warning("Plugin '%s' not available - check your instalation", skel_args['plugin_name'])

        skel_args['jinja_env'] = plugin_storage.get_jinja_env()

        # TODO: Use json schema or another validation method
        skel_obj = NotificationSkeleton(**skel_args)
        json_data['skeleton'] = skel_obj  # replace json data with skeleton instance

        return cls(**json_data)

    @classmethod
    def validate_version(cls, data):
        """Validate version of stored notification based on API version"""
        if 'api_version' not in data:
            logger.warning("Notification doesn't contain API version")
            return False

        if not isinstance(data['api_version'], int):
            logger.warning("API version is not number")
            return False

        if data['api_version'] < cls.API_VERSION:
            logger.warning("Notification was created using older API")
            return False

        return True

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
            return self.skeleton.render(self.data, media_type, lang)
        except TemplateError:
            raise NotificationTemplatingError("Failed to render template")
        except NoSuchTemplateError:
            raise NotificationTemplatingError("Could not find template file")

    def render(self, media_type, lang):
        """Return rendered template as given media type and in given language"""
        output = {}
        output['actions'] = self.skeleton.translate_actions(lang)

        if self.explicit_dismiss:
            output['actions']['dismiss'] = ''  # default action for all notifications
        output['metadata'] = self._serialize_data(self.META_ATTRS)

        try:
            output['message'] = self.render_template(media_type, lang)
            return output
        except NotificationTemplatingError:
            if media_type not in self.fallback:
                output['message'] = self.fallback['plain']
            else:
                output['message'] = self.fallback[media_type]
            return output

    def render_fallback_data(self):
        """Render all media types in default languages"""
        ret = {}
        try:

            for mt in self.skeleton.get_media_types():
                # render in default lang -> en
                ret[mt] = self.render_template(mt, 'en')

        except NotificationTemplatingError:
            raise CreateNotificationError("Couldn't create notification with given template variables")

        return ret

    def _serialize_data(self, attrs):
        """Return serialized attributes of instance in dictionary"""
        out = {}

        for attr in attrs:
            data = getattr(self, attr)
            if hasattr(data, 'serialize'):
                data = data.serialize()

            out[attr] = data

        return out

    def serialize(self):
        """Return serialized data as json"""
        return json.dumps(self._serialize_data(self.ATTRS), indent=4)

    def get_data(self):
        """Return instance content as SimpleNamespace"""
        return SimpleNamespace(**self._serialize_data(self.ATTRS))

    def _dismiss(self):
        """
        Internal dismiss function

        Mark notification for deletion
        """
        self.valid = False

    def dismiss(self):
        """Dismiss notification if explicit dismiss is allowed"""
        if not self.explicit_dismiss:
            return None

        self._dismiss()
        return True

    def _run_cmd_standalone(self, cmd, cmd_args, timeout):
        """
        Run command in new standalone process

        Process is supervised to control it's run a little bit
        """
        supervisor = Supervisor()
        supervisor.run(cmd, cmd_args, timeout)

    def call_action(self, name, plugin_skeleton, cmd_args=None, dry_run=True):
        action_cmd = self.skeleton.get_action_cmd(name)

        if not action_cmd:
            logger.debug("Action '%s' not available", name)
            return False

        if dry_run:
            logger.debug("Dry run: executing command '%s'", action_cmd)
        else:
            if name not in plugin_skeleton.actions.keys():
                logger.warning("Action is not presented in current version of plugin. Won't execute")
            elif self.skeleton.version != plugin_skeleton.version:
                logger.warning("Using outdated action. Won't execute")
            else:
                timeout = config.getint('settings', 'cmd_timeout')
                self._run_cmd_standalone(action_cmd, cmd_args, timeout)

        self._dismiss()
        return True

    def get_default_action(self):
        return self.default_action

    def has_action(self, name):
        if name == 'default':
            return True
        elif name == 'dismiss':
            return self.explicit_dismiss

        return self.skeleton.is_valid_action(name)

    def has_media_type(self, media_type):
        return media_type in self.skeleton.get_media_types()

    @staticmethod
    def _generate_id():
        """
        Generate unique id of message based on uuid

        Returned as string
        """
        return uuid.uuid4().hex
