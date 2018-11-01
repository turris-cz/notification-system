import os.path

from .config import config
from .exceptions import (
    MediaTypeNotAvailableException,
    NoSuchActionException,
    NoSuchNotificationException,
    NotificationNotDismissibleException
)
from .pluginstorage import PluginStorage
from .logger import logger
from .notificationstorage import NotificationStorage
from .notification import Notification


class Api:
    """Public interface of module"""

    def __init__(self, conf=None):
        if conf:  # override default config
            config.load_config(conf)

        plugin_dir = config.get('settings', 'plugin_dir')
        templates_dir = config.get('settings', 'templates_dir')
        volatile_dir = config.get('settings', 'volatile_dir')
        persistent_dir = config.get('settings', 'persistent_dir')

        if not os.path.exists(plugin_dir):
            logger.error("Missing plugin directory %s", plugin_dir)
            raise NotADirectoryError("Missing plugin directory {}".format(plugin_dir))

        if not os.path.exists(templates_dir):
            logger.error("Missing templates directory %s", templates_dir)
            raise NotADirectoryError("Missing templates directory {}".format(templates_dir))

        if not os.path.exists(volatile_dir):
            logger.error("Missing volatile messages directory %s", volatile_dir)
            raise NotADirectoryError("Missing volatile messages directory {}".format(volatile_dir))

        if not os.path.exists(persistent_dir):
            logger.error("Missing persistent messages directory %s", persistent_dir)
            raise NotADirectoryError("Missing persistent messages directory {}".format(persistent_dir))

        self.plugins = PluginStorage(plugin_dir, templates_dir)
        self.notifications = NotificationStorage(volatile_dir, persistent_dir)

    def get_notifications(self, media_type='simple', lang='en'):
        """Return all notifications"""
        self.notifications.delete_invalid_messages()

        return self.notifications.get_all_rendered(media_type, lang)

    def get_rendered_notification(self, msgid, media_type, lang, force_media_type=False):
        """Get rendered notification of specific media type by id"""
        self.notifications.delete_invalid_messages()

        if self.notifications.valid_id(msgid):
            rendered = self.notifications.get_rendered(msgid, media_type, lang, force_media_type)

            if not rendered:
                logger.debug("Notification cannot be rendered in media type '%s'", media_type)
                raise MediaTypeNotAvailableException("Notification does not have media type '{}'".format(media_type))

            return rendered

        raise NoSuchNotificationException("Notification ID '{}' does not exist".format(msgid))

    def get_templates(self):
        """Return notification types from plugins"""
        return self.plugins.get_notification_types()

    # data manipulation
    def store(self, n):
        """Store already created notification"""
        self.notifications.store(n)

    def create(self, skel_id, **user_opts):
        """
        Create new notification based on selected skeleton

        Prefered method for creating notification with minimal knowledge of underlying layers
        """
        logger.debug("Create new notification: chosen skeleton: %s", skel_id)
        logger.debug("Create new notification: user opts entered: %s", user_opts)

        skel = self.plugins.get_skeleton(skel_id)

        if not skel:
            return None

        notification_defaults = skel.get_skeleton_defaults()
        notification_defaults.update(user_opts)

        notif = Notification.new(skel, **notification_defaults)
        self.notifications.store(notif)

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
                    raise NotificationNotDismissibleException
            else:
                success = n.call_action(name, cmd_args, False)

                if not success:
                    raise NoSuchActionException("Notification does not have action '{}'".format(name))

            self.notifications.remove(msgid)
        else:
            raise NoSuchNotificationException("{}".format(msgid))
