import os

from .plugin import Plugin
from .logger import logger
from .notificationskeleton import NotificationSkeleton


class PluginStorage:
    """Storage for plugins"""

    def __init__(self, plugin_dir, templates_dir):
        # print("Constructing new PluginStorage")
        self.plugin_dir = plugin_dir
        self.templates_dir = templates_dir

        self.plugins = {}
        self.skeletons = {}

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
                self.plugins[p.name] = p

    def get_plugin(self, name):
        """Return plugin specified by name"""
        return self.plugins[name]

    def get_all(self):
        """Return all plugins"""
        return self.plugins

    def get_skeleton(self, skel_id):
        """
        Return notification skeleton based on id

        input param in form 'PluginName.skeletonid'
        so it need to be parsed to get skel_id

        skeleton object either exists cached or will be added when needed
        """
        plugin_name, skel_name = skel_id.split('.')

        if skel_id not in self.skeletons:
            if plugin_name in self.plugins:
                notification_types = self.plugins[plugin_name].get_notification_types()
                templates = self.plugins[plugin_name].get_templates()

                if skel_name in notification_types:
                    # TODO: refactor/simplify this code
                    notification_args = {}
                    notification_args['name'] = notification_types[skel_name]['name']
                    notification_args['plugin_name'] = plugin_name

                    skel_actions = {}
                    plugin_actions = self.plugins[plugin_name].get_actions()
                    for action in notification_types[skel_name]['actions']:
                        if action in plugin_actions:
                            skel_actions[action] = plugin_actions[action]

                    notification_args['actions'] = skel_actions

                    tmpl_name = notification_types[skel_name]['template']
                    template = templates[tmpl_name]
                    notification_args['template'] = template

                    if 'timeout' in notification_types[skel_name]:
                        notification_args['timeout'] = notification_types[skel_name]['timeout']
                    if 'severity' in notification_types[skel_name]:
                        notification_args['severity'] = notification_types[skel_name]['severity']
                    if 'persistent' in notification_types[skel_name]:
                        notification_args['persistent'] = notification_types[skel_name]['persistent']

                    notification_args['template_dir'] = os.path.join(self.templates_dir, plugin_name)
                    self.skeletons[skel_id] = NotificationSkeleton(**notification_args)  # cache it
                # else:
                #     logger.warn("No such notification type '%s' in plugin '%s'", skel_name, plugin_name)
                #     return what?
            # else:
            #     logger.warn("No such skeleton: '%s'", skel_id)
            #     return what?

        return self.skeletons[skel_id]

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
