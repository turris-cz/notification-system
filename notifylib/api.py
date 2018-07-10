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
            config.get('settings', 'persistent_dir'),
            config.get('settings', 'volatile_dir'),
            self.plugins.get_notification_types()
        )

        print("Debug: Available notification_types: {}".format(self.notifications.notification_types))

    def init_logger(self):
        """Init new logger instance"""
        pass

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

    # data manipulation
    def create(self, **user_opts):
        """Create new notification"""
        # get pre-filled skeleton of class Notification
        print(user_opts)
        notif = self.notifications.get_skeleton(user_opts['template'])

        self.notifications.store(notif)

    # TODO: refactor
    def call_action(self, mgsid, name, **kwargs):
        """Call action on notification"""
        pass
        # storage.actions[name](**kwargs)

    def dismiss(self, msgid):
        """Dismiss specific notification"""
        self.call_action(msgid, 'dismiss')
