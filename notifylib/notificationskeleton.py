import gettext

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

    def get_action(self, name):
        if name in self.actions:
            return self.actions[name]['command']

        return None

    def translate_actions(self, lang):
        actions = {}

        for a in self.actions:
            actions[a] = self._translate(self.actions[a]['title'], lang)

        return actions

    def _translate(self, message, lang):
        """Translate single variable content"""
        transl = self._get_translation(lang)

        if transl:
            transl.install()

            translated = gettext.gettext(_(message))

            # reset translation to default
            transl = gettext.NullTranslations()
            transl.install()

            return translated

        return message

    def _fetch_translation(self, lang):
        self.translations[lang] = gettext.translation(self.plugin_name, localedir='locale', languages=[lang])

    def _get_translation(self, lang):
        if lang in self.translations:
            return self.translations[lang]

        try:
            self._fetch_translation(lang)
            return self.translations[lang]
        except FileNotFoundError:
            return None

    def _set_jinja_translation(self, lang):
        """
        Set gettext translation for jinja env

        Try to load translation otherwise use NullTranslations
        """
        transl = self._get_translation(lang)

        if transl:
            self.jinja_env.install_gettext_translations(transl, newstyle=True)
        else:
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
        self._set_jinja_translation(lang)
        output = self.jinja_template.render(media=media_type, **data)

        return output

    def __str__(self):
        out = "{\n"

        for attr in self.ATTRS:
            out += "\t{}: {}\n".format(attr, getattr(self, attr))

        out += "}\n"

        return out
