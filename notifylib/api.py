import logging

from .config import config
from .pluginstorage import PluginStorage
from .notificationstorage import NotificationStorage


class Api:
    """Public interface of module"""
    def __init__(self, conf=None):
        print("Creating instance of API")
        self.init_logger()

        if conf:  # override default config
            config.load_config(conf)

        self.plugins = PluginStorage(config.get('settings', 'plugin_dir'))
        self.notifications = NotificationStorage(
            config.get('settings', 'volatile_dir'),
            config.get('settings', 'persistent_dir'),
            self.plugins.get_notification_types()
        )

        # self.logger.debug("Available notification_types: %s" % self.notifications.notification_types)

    def init_logger(self):
        """Init new logger instance"""
        self.logger = logging.getLogger("notifylib")

    def get_plugins(self):
        return self.plugins.get_all()

    def get_actions(self, plug_name):
        """Get actions of specified plugin"""
        return self.plugins.get_plugin(plug_name).get_actions()

    def get_notifications(self):
        return self.notifications.get_all()

    def get_notification(self, msgid):
        """Show notification of one specific by id"""
        if msgid:
            return self.notifications.get_notification(msgid)

    def get_templates(self):
        """Return notification types from plugins"""
        return self.notifications.get_notification_types()

    # data manipulation
    def create(self, **user_opts):
        """Create new notification"""
        # get pre-filled skeleton of class Notification
        self.logger.debug("Create new notification; user opts entered: %s" % user_opts)

        notif = self.notifications.get_new_instance(**user_opts)

        print("Newly created notification: {}".format(notif))

        self.notifications.store(notif)

        self.logger.debug("Stored notifications: %s" % self.notifications.get_all())

    # TODO: refactor
    def call_action(self, mgsid, name, **kwargs):
        """Call action on notification"""
        pass
        # storage.actions[name](**kwargs)

    def dismiss(self, msgid):
        """Dismiss specific notification"""
        self.call_action(msgid, 'dismiss')
