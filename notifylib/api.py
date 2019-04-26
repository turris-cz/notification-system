import logging

from pathlib import Path
from .config import config
from .exceptions import (
    MediaTypeNotAvailableError,
    NoSuchActionError,
    NoSuchNotificationError,
    NoSuchNotificationSkeletonError,
    NotificationNotDismissibleError,
    NotificationStorageError,
    InvalidOptionsError,
)
from .pluginstorage import PluginStorage
from .notificationstorage import NotificationStorage
from .notification import Notification
from .severity import Severity

logger = logging.getLogger(__name__)


class Api:
    """Public interface of module"""

    def __init__(self, conffile=None, confdict=None):
        # override default config
        if conffile:
            config.load_from_file(conffile)
        elif confdict:
            config.load_from_dict(confdict)

        plugin_dir = config.get('settings', 'plugin_dir')
        volatile_dir = config.get('settings', 'volatile_dir')
        persistent_dir = config.get('settings', 'persistent_dir')

        if not Path(plugin_dir).is_dir():
            logger.error("Missing plugin directory %s", plugin_dir)
            raise NotADirectoryError("Missing plugin directory {}".format(plugin_dir))

        for name, storage_path in {'persistent': volatile_dir, 'volatile': persistent_dir}.items():
            p = Path(storage_path)
            if not p.is_dir():
                logger.info("Missing %s messages directory '%s', recreating it", name, storage_path)
                p.mkdir(parents=True, exist_ok=True)

        self.plugins = PluginStorage(plugin_dir)
        self.notifications = NotificationStorage(volatile_dir, persistent_dir, self.plugins)

    def get_notifications(self, media_type='plain', lang='en'):
        """Return all notifications"""
        self.notifications.delete_invalid_messages()

        return self.notifications.get_all_rendered(media_type, lang)

    def get_rendered_notification(self, msgid, media_type='plain', lang='en', force_media_type=False):
        """Get rendered notification of specific media type by id"""
        self.notifications.delete_invalid_messages()

        if self.notifications.valid_id(msgid):
            rendered = self.notifications.get_rendered(msgid, media_type, lang, force_media_type)

            if not rendered:
                raise MediaTypeNotAvailableError("Notification does not have media type '{}'".format(media_type))

            return rendered

        raise NoSuchNotificationError("Notification with ID '{}' does not exist".format(msgid))

    def get_templates(self):
        """Return notification types from plugins"""
        return self.plugins.get_notification_types()

    # data manipulation
    def store(self, n):
        """Store already created notification"""
        return self.notifications.store(n)

    def create(self, skel_id, **user_opts):
        """
        Create new notification based on selected skeleton

        Prefered method for creating notification with minimal knowledge of underlying layers
        """
        logger.debug("Create new notification: chosen skeleton: %s", skel_id)
        logger.debug("Create new notification: user opts entered: %s", user_opts)

        skel = self.plugins.get_skeleton(skel_id)

        if not skel:
            raise NoSuchNotificationSkeletonError

        self.validate_user_opts(user_opts)

        notification_defaults = skel.get_skeleton_defaults()
        notification_defaults.update(user_opts)

        notif = Notification.new(skel, **notification_defaults)
        success = self.notifications.store(notif)

        if not success:
            raise NotificationStorageError

        return notif.notif_id

    def call_action(self, msgid, name, cmd_args=None):
        """Call action on notification"""
        self.notifications.delete_invalid_messages()

        n = self.notifications.get(msgid)

        if n:
            if name == 'default':
                name = n.get_default_action()
                logger.debug("Using default action: '%s'", name)

            if name == 'dismiss':
                success = n.dismiss()

                if not success:
                    raise NotificationNotDismissibleError
            else:
                skeleton_id = '{}.{}'.format(n.skeleton.plugin_name, n.skeleton.name)
                skel = self.plugins.get_skeleton(skeleton_id)
                success = n.call_action(name, skel, cmd_args, False)

                if not success:
                    raise NoSuchActionError("Notification does not have action '{}'".format(name))

            self.notifications.remove(msgid)
        else:
            raise NoSuchNotificationError("Notification with ID '{}' does not exist".format(msgid))

    def validate_user_opts(self, opts):
        # TODO: validate all user entered options properly
        if 'severity' in opts and opts['severity'] not in Severity.STANDARD:
            logger.warning("Invalid severity level '%s'", opts['severity'])
            raise InvalidOptionsError("Invalid severity level '{}'".format(opts['severity']))
