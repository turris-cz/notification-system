import gettext
import shlex
import subprocess

import jinja2


class NotificationSkeleton:
    ATTRS = ['name', 'plugin_name', 'template', 'actions', 'template_dir', 'timeout', 'severity', 'persistent']

    def __init__(self, name, plugin_name, template, actions, template_dir, timeout=None, severity='info', persistent=False):
        self.name = name
        self.plugin_name = plugin_name
        self.template = template
        self.actions = actions
        self.template_dir = template_dir

        self.timeout = timeout
        self.severity = severity
        self.persistent = persistent

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
        defaults = {
            'timeout': self.timeout,
            'severity': self.severity,
            'persistent': self.persistent,
        }

        return defaults

    def call_action(self, name, dry_run=False):
        if name in self.actions:
            action = self.actions[name]['command']

            if dry_run:
                print("Dry run: executing command '{}'".format(action))
            else:
                # TODO: validate command string somehow
                cmd = shlex.split(action)
                res = subprocess.run(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

                if res.returncode != 0:
                    print("Command failed with exit code {}".format(res.returncode))
                    print("stdout: {}".format(res.stdout))
                    print("stderr: {}".format(res.stderr))
                else:
                    print("Command exited succesfully")

    def _get_translation(self, lang):
        self.translations[lang] = gettext.translation(self.plugin_name, localedir='locale', languages=[lang])

    def _set_translation(self, lang):
        """
        Set gettext translation for jinja env

        Try to load translation otherwise use NullTranslations
        """

        if lang in self.translations:
            self.jinja_env.install_gettext_translations(self.translations[lang], newstyle=True)
        else:
            try:
                self._get_translation(lang)
                self.jinja_env.install_gettext_translations(self.translations[lang], newstyle=True)
            except FileNotFoundError:
                self.jinja_env.install_null_translations()

    def init_jinja_env(self):
        """
        Init jinja environment

        Prepare template for later use
        For now it will be initiated when creating new skeleton instance
        """
        template_loader = jinja2.FileSystemLoader(self.template_dir)
        self.jinja_env = jinja2.Environment(
            loader=template_loader,
            extensions=['jinja2.ext.i18n']
        )
        self.jinja_template = self.jinja_env.get_template(self.template['src'])

    def render(self, media_type, lang, data):
        """Render using jinja in given language"""
        self._set_translation(lang)
        output = self.jinja_template.render(media=media_type, **data)

        return output

    def __str__(self):
        out = "{\n"

        for attr in self.ATTRS:
            out += "\t{}: {}\n".format(attr, getattr(self, attr))

        out += "}\n"

        return out
