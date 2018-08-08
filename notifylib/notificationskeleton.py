import jinja2


class NotificationSkeleton:
    ATTRS = ['name', 'template', 'actions', 'template_dir']

    def __init__(self, name, template, actions, template_dir):
        self.name = name
        self.template = template
        self.actions = actions
        self.template_dir = template_dir

        self.init_jinja_env()

    def get_media_types(self):
        return self.template['supported_media']

    def serialize(self):
        json_data = {}

        for attr in self.ATTRS:
            json_data[attr] = getattr(self, attr)

        return json_data

    def init_jinja_env(self):
        """
        Init jinja environment

        Prepare template for later use
        For now it will be initiated in when creating new skeleton instance
        """
        template_loader = jinja2.FileSystemLoader(searchpath=self.template_dir)
        template_env = jinja2.Environment(loader=template_loader)
        self.jinja_template = template_env.get_template(self.template['src'])

    def render(self, media_type, lang, **jinja_vars):
        """Render using jinja"""
        jinja_vars['media'] = media_type

        # TODO: render with babel/gettext

        output = self.jinja_template.render(**jinja_vars)

        return output

    def __str__(self):
        out = "{\n"
        out += "\tname: {}\n".format(self.name)
        out += "\ttemplate: {}\n".format(self.template)
        out += "\tactions: {}\n".format(self.actions)
        out += "}\n"

        return out
