import gettext
import logging
import os

import yaml

from jinja2 import TemplateNotFound
from .exceptions import NoSuchTemplateException

logger = logging.getLogger(__name__)


class NotificationSkeleton:
    ATTRS = ['name', 'plugin_name', 'version', 'template', 'actions', 'timeout', 'severity', 'persistent', 'explicit_dismiss']
    DEFAULT_ATTRS = ['timeout', 'severity', 'persistent', 'explicit_dismiss']

    def __init__(self, name, plugin_name, version, template, actions, jinja_env, timeout=None, severity='info', persistent=False, explicit_dismiss=True):
        self.name = name
        self.plugin_name = plugin_name
        self.version = version
        self.template = template
        self.actions = actions
        self.timeout = timeout
        self.severity = severity
        self.persistent = persistent
        self.explicit_dismiss = explicit_dismiss

        self.fallback = False
        self.jinja_env = jinja_env
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

        if self.fallback:
            translated = []

            for action in self.actions.values():
                tpl = self.jinja_env.from_string(action['title'])
                action['title'] = tpl.render()
                translated.append(action)

            parsed = {'actions': translated}
        else:
            parsed = yaml.safe_load(self.jinja_plugin_template.render())

        return {
            pa['name']: pa['title'] for pa in parsed['actions'] if pa['name'] in self.actions
        }

    def setup_jinja_env(self):
        """Prepare templates for later use"""
        try:
            self.jinja_message_template = self.jinja_env.get_template(os.path.join(self.plugin_name, 'templates', self.template['src']))

            self.jinja_plugin_template = self.jinja_env.get_template(os.path.join(self.plugin_name, 'plugin.yml'))
        except TemplateNotFound as e:
            self.fallback = True
            logger.warning("Template file '%s' not found", e)
            logger.debug("Using fallback instead")

    def _set_jinja_translation(self, lang):
        self.jinja_env.install_gettext_translations(
            gettext.translation("notification-system", localedir='/usr/share/locale', languages=[lang], fallback=True)
        )

    def render(self, data, media_type, lang):
        """Render using jinja in given language"""
        if self.fallback:
            raise NoSuchTemplateException

        self._set_jinja_translation(lang)
        output = self.jinja_message_template.render(media=media_type, **data)

        return output
