import os
import logging

from functools import lru_cache

from .plugin import Plugin
from .notificationskeleton import NotificationSkeleton

logger = logging.getLogger(__name__)


class PluginStorage:
    """Storage for plugins"""
    META_ATTRS = ['name', 'version', 'timeout', 'severity', 'persistent', 'explicit_dismiss']

    def __init__(self, plugin_dir, templates_dir):
        # print("Constructing new PluginStorage")
        self.plugin_dir = plugin_dir
        self.templates_dir = templates_dir

        self.plugins = {}

        self.load()

    def plugin_file_path(self, f):
        """Return full path of plugin file"""
        return os.path.join(self.plugin_dir, f)

    def load(self):
        """Load plugins from FS"""
        for _, _, files in os.walk(self.plugin_dir):
            for f in files:
                if f.startswith('.'):  # ignore dotfiles
                    continue

                p = Plugin.from_file(self.plugin_file_path(f))

                if p:
                    self.plugins[p.name] = p

    def get_plugin(self, name):
        """Return plugin specified by name"""
        return self.plugins[name]

    def get_all(self):
        """Return all plugins"""
        return self.plugins

    def valid_id(self, skel_id):
        try:
            plugin_name, skel_name = skel_id.split('.')
        except ValueError:
            logger.warning("Malformed skeleton id '%s'", skel_id)
            return False

        if plugin_name not in self.plugins:
            logger.warning("No such plugin '%s'", plugin_name)
            return False

        if skel_name not in self.plugins[plugin_name].get_notification_types():
            logger.warning("No such skeleton: '%s'", skel_name)
            return False

        return True

    @lru_cache(maxsize=256)
    def get_skeleton(self, skel_id):
        """
        Return notification skeleton based on id

        input param in form 'PluginName.SkeletonName'
        so it need to be parsed to get skel_id

        skeleton object either exists cached or will be added when needed
        """

        if not self.valid_id(skel_id):
            return None

        plugin_name, skel_name = skel_id.split('.')

        plugin = self.plugins[plugin_name]

        notification_types = plugin.get_notification_types()
        plugin_actions = plugin.get_actions()
        templates = plugin.get_templates()

        skeleton = notification_types[skel_name]

        # TODO: refactor/simplify this code
        notification_args = {}
        notification_args['plugin_name'] = plugin_name

        skel_actions = {}
        for action in skeleton['actions']:
            if action in plugin_actions:
                skel_actions[action] = plugin_actions[action]

        notification_args['actions'] = skel_actions

        tmpl_name = skeleton['template']
        template = templates[tmpl_name]
        notification_args['template'] = template

        for attr in self.META_ATTRS:
            if attr in skeleton:
                notification_args[attr] = skeleton[attr]

        notification_args['template_dir'] = os.path.join(self.templates_dir, plugin_name)

        return NotificationSkeleton(**notification_args)

    def get_notification_types(self):
        """Return all notification types from plugins"""
        ret = []

        for name, plugin in self.plugins.items():
            logger.debug("%s - %s", name, plugin)

            args = plugin.get_notification_types()

            logger.debug("Plugin metadata: %s", args)

            type_names = ["{}.{}".format(name, type_name) for type_name in args.keys()]
            ret.extend(type_names)

        return ret
