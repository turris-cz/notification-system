import logging

from .config import config
from .pluginstorage import PluginStorage
from .notificationstorage import NotificationStorage
from .notification import Notification


class Api:
    """Public interface of module"""
    def __init__(self, conf=None):
        self.init_logger()

        if conf:  # override default config
            config.load_config(conf)

        self.plugins = PluginStorage(config.get('settings', 'plugin_dir'))
        self.notifications = NotificationStorage(
            config.get('settings', 'volatile_dir'),
            config.get('settings', 'persistent_dir'),
        )

    def init_logger(self):
        """Init new logger instance"""
        self.logger = logging.getLogger("notifylib")

    def list_plugins(self):
        """List of plugin names to client code"""
        return self.plugins.get_all().keys()

    def get_actions(self, plug_name):
        """Get actions of specified plugin"""
        return self.plugins.get_plugin(plug_name).get_actions()

    def get_notifications(self):
        return self.notifications.get_all()

    def get_notification(self, msgid):
        """Show notification of one specific by id"""
        return self.notifications.get_notification(msgid)

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
        # get pre-filled skeleton of class Notification
        self.logger.debug("Create new notification: chosen skeleton: %s" % skel_id)
        self.logger.debug("Create new notification: user opts entered: %s" % user_opts)

        skel = self.plugin.get_skeleton(skel_id)
        notif = Notification.new(skel, **user_opts)

        # print("Newly created notification: {}".format(notif))

        self.notifications.store(notif)

        # self.logger.debug("Stored notifications: %s" % self.notifications.get_all())

    # TODO: rethink/refactor
    def call_action(self, mgsid, name, **kwargs):
        """Call action on notification"""
        pass
        # storage.actions[name](**kwargs)

    def dismiss(self, msgid):
        """Dismiss specific notification"""
        self.call_action(msgid, 'dismiss')
