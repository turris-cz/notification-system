import gettext

import yaml


class NotificationSkeleton:
    ATTRS = ['name', 'plugin_name', 'version', 'template', 'actions', 'timeout', 'severity', 'persistent', 'explicit_dismiss']
    DEFAULT_ATTRS = ['timeout', 'severity', 'persistent', 'explicit_dismiss']

    def __init__(self, name, plugin_name, version, template, actions, jinja_env, timeout=None, severity='info', persistent=False, explicit_dismiss=True):
        self.name = name
        self.plugin_name = plugin_name
        self.version = version
        self.template = template
        self.actions = actions
        self.jinja_env = jinja_env

        self.timeout = timeout
        self.severity = severity
        self.persistent = persistent
        self.explicit_dismiss = explicit_dismiss

        self.setup_jinja_env()
        self.translations = {}

    def get_media_types(self):
        return self.template['supported_media']

    def serialize(self):
        json_data = {}

        for attr in self.ATTRS:
            json_data[attr] = getattr(self, attr)

        return json_data

    def get_skeleton_defaults(self):
        defaults = {}

        for attr in self.DEFAULT_ATTRS:
            defaults[attr] = getattr(self, attr)

        return defaults

    def get_action_cmd(self, name):
        if name in self.actions:
            return self.actions[name]['command']

        return None

    def translate_actions(self, lang):
        self._set_jinja_translation(lang)

        parsed = yaml.safe_load(self.jinja_plugin_template.render())
        return {
            pa['name']: pa['title'] for pa in parsed['actions'] if pa['name'] in self.actions
        }

    def setup_jinja_env(self):
        """Prepare templates for later use"""
        self.jinja_message_template = self.jinja_env.get_template(self.template['src'])

        plugin_template = '{}.yml'.format(self.plugin_name)
        self.jinja_plugin_template = self.jinja_env.get_template(plugin_template)

    def _set_jinja_translation(self, lang):
        self.jinja_env.install_gettext_translations(
            gettext.translation("notifylib-{}".format(self.plugin_name), localedir='/usr/share/locale', languages=[lang], fallback=True)
        )

    def render(self, data, media_type, lang):
        """Render using jinja in given language"""
        self._set_jinja_translation(lang)
        output = self.jinja_message_template.render(media=media_type, **data)

        return output

    def __str__(self):
        out = "{\n"

        for attr in self.ATTRS:
            out += "\t{}: {}\n".format(attr, getattr(self, attr))

        out += "}\n"

        return out
