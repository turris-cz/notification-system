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

    def delete_invalid_messages(self):
        """Delete all invalid messages in storage"""
        self.notifications.delete_invalid_messages()

    def get_actions(self, plug_name):
        """Get actions of specified plugin"""
        return self.plugins.get_plugin(plug_name).get_actions()

    def get_notifications(self):
        """Return all notifications"""
        self.delete_invalid_messages()
        return self.notifications.get_all()

    def get_notification(self, msgid, media_type, lang):
        """Show notification of one specific by id"""
        self.delete_invalid_messages()
        return self.notifications.get_notification(msgid, media_type, lang)

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

    # TODO: rethink/refactor
    def call_action(self, mgsid, name, **kwargs):
        """Call action on notification"""
        pass
        # storage.actions[name](**kwargs)

    def dismiss(self, msgid):
        """Dismiss specific notification"""
        self.call_action(msgid, 'dismiss')
