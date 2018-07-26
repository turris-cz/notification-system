import jinja2


class NotificationSkeleton:
    def __init__(self, name, template, actions):
        self.name = name
        self.template = template
        self.actions = actions

    def get_media_types(self):
        return self.template['supported_media']

    def serialize(self):
        json_data = {
            'name': self.name,
            'template': self.template,
            'actions': self.actions,
        }

        return json_data

    def render(self, media_type, lang, content):
        """Render using jinja"""
        tmpl_dir, tmpl_file = self.template['src'].rsplit('/', 1)

        templateLoader = jinja2.FileSystemLoader(searchpath=tmpl_dir)
        templateEnv = jinja2.Environment(loader=templateLoader)

        template = templateEnv.get_template(tmpl_file)
        output = template.render(media=media_type, message=content)

        return output

    def __str__(self):
        out = "{\n"
        out += "\tname: {}\n".format(self.name)
        out += "\ttemplate: {}\n".format(self.template)
        out += "\tactions: {}\n".format(self.actions)
        out += "}\n"

        return out
