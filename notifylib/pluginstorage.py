import os
import logging

from .plugin import Plugin
from .notificationskeleton import NotificationSkeleton


class PluginStorage:
    """Storage for plugins"""
    def __init__(self, plugin_dir):
        print("Constructing new PluginStorage")
        self.plugin_dir = plugin_dir
        self.init_logger()

        self.plugins = {}
        self.load()

    def init_logger(self):
        self.logger = logging.getLogger("notifylib")

    def plugin_file_path(self, f):
        return os.path.join(self.plugin_dir, f)

    def load(self):
        """Load plugins from FS"""
        for root, dirs, files in os.walk(self.plugin_dir):
            for f in files:
                if f.startswith('.'):  # ignore dotfiles
                    continue

                p = Plugin.from_file(self.plugin_file_path(f))
                self.plugins[p.name] = p

    def get_plugin(self, name):
        return self.plugins[name]

    def get_all(self):
        """Return all plugins"""
        return self.plugins

    def get_notification_types(self):
        ret = {}

        for name, plugin in self.plugins.items():
            self.logger.debug("%s - %s" % (name, plugin))

            args = plugin.get_notification_types()

            self.logger.debug("Plugin metadata: %s" % args)

            for n_name, n_data in args.items():
                self.logger.debug("Notif data: %s" % n_data)
                ret[n_name] = NotificationSkeleton(**n_data)

        return ret
