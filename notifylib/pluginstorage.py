import os

from .plugin import Plugin


class PluginStorage:
    """Storage for plugins"""
    def __init__(self, plugin_dir):
        print("Constructing new PluginStorage")
        self.plugin_dir = plugin_dir
        self.init_logger()

        self.plugins = {}
        self.load()

    def init_logger(self):
        pass

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

            # don't walk into lower levels
            break

    def get_plugin(self, name):
        return self.plugins[name]

    def get_all(self):
        """Return all plugins"""
        return self.plugins

    def get_notification_types(self):
        ret = {}

        for k, v in self.plugins.items():
            ret[k] = v.get_notification_types()

        return ret
