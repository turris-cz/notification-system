import gettext

import jinja2
import yaml


class NotificationSkeleton:
    ATTRS = ['name', 'plugin_name', 'version', 'template', 'actions', 'template_dirs', 'timeout', 'severity', 'persistent', 'explicit_dismiss']
    DEFAULT_ATTRS = ['timeout', 'severity', 'persistent', 'explicit_dismiss']

    def __init__(self, name, plugin_name, version, template, actions, template_dirs, timeout=None, severity='info', persistent=False, explicit_dismiss=True):
        self.name = name
        self.plugin_name = plugin_name
        self.version = version
        self.template = template
        self.actions = actions
        self.template_dirs = template_dirs

        self.timeout = timeout
        self.severity = severity
        self.persistent = persistent
        self.explicit_dismiss = explicit_dismiss

        self.init_jinja_env()
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

        actions = {}

        parsed = yaml.safe_load(self.jinja_plugin_template.render())
        for a in self.actions:
            for pa in parsed['actions']:
                if a == pa['name']:
                    actions[a] = pa['title']

        return actions

    def init_jinja_env(self):
        """
        Init jinja environment

        Prepare template for later use
        For now it will be initiated when creating new skeleton instance
        """
        template_loader = jinja2.FileSystemLoader(self.template_dirs)
        self.jinja_env = jinja2.Environment(
            loader=template_loader,
            autoescape=True,
            extensions=['jinja2.ext.i18n']
        )

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
