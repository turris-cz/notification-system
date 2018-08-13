import jinja2


class NotificationSkeleton:
    ATTRS = ['name', 'template', 'actions', 'template_dir', 'timeout', 'severity', 'persistent']

    def __init__(self, name, template, actions, template_dir, timeout=None, severity='info', persistent=False):
        self.name = name
        self.template = template
        self.actions = actions
        self.template_dir = template_dir

        self.timeout = timeout
        self.severity = severity
        self.persistent = persistent

        self.init_jinja_env()

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

    def init_jinja_env(self):
        """
        Init jinja environment

        Prepare template for later use
        For now it will be initiated in when creating new skeleton instance
        """
        template_loader = jinja2.FileSystemLoader(searchpath=self.template_dir)
        template_env = jinja2.Environment(loader=template_loader)
        self.jinja_template = template_env.get_template(self.template['src'])

    def render(self, media_type, lang, data):
        """Render using jinja"""
        # TODO: render with babel/gettext

        output = self.jinja_template.render(media=media_type, **data)

        return output

    def __str__(self):
        out = "{\n"

        for attr in self.ATTRS:
            out += "\t{}: {}\n".format(attr, getattr(self, attr))

        out += "}\n"

        return out
