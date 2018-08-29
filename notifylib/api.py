from .config import config
from .pluginstorage import PluginStorage
from .logger import logger
from .notificationstorage import NotificationStorage
from .notification import Notification


class Api:
    """Public interface of module"""

    def __init__(self, conf=None):
        if conf:  # override default config
            config.load_config(conf)

        self.plugins = PluginStorage(
            config.get('settings', 'plugin_dir'),
            config.get('settings', 'templates_dir'),
        )
        self.notifications = NotificationStorage(
            config.get('settings', 'volatile_dir'),
            config.get('settings', 'persistent_dir'),
        )

    def get_notifications(self):
        """Return all notifications"""
        self.notifications.delete_invalid_messages()
        notifications = self.notifications.get_all()

        return {k: v.get_data() for k, v in notifications.items()}

    def get_rendered_notification(self, msgid, media_type, lang):
        """Get rendered notification of specific media type by id"""
        self.notifications.delete_invalid_messages()
        return self.notifications.get_rendered(msgid, media_type, lang)

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

        notification_defaults = skel.get_skeleton_defaults()
        notification_defaults.update(user_opts)

        notif = Notification.new(skel, **notification_defaults)
        self.notifications.store(notif)

    def call_action(self, msgid, name):
        """Call action on notification"""
        self.notifications.delete_invalid_messages()

        n = self.notifications.get(msgid)

        if name == 'dismiss':
            n.dismiss()
            self.notifications.remove(msgid)
        else:
            n.call_action(name)
