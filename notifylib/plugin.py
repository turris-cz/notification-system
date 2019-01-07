import logging
import os
import pathlib

import jinja2
import yaml

logger = logging.getLogger(__name__)


class Plugin:
    SCHEMA = {
        'actions': ['name', 'title', 'command'],
        'templates': ['type', 'supported_media', 'src'],
    }
    # 'notifications' section is intentionally omitted for now
    # until mandatory and optional attributes check for 'notifications' is implemented

    def __init__(self, name, template_dirs, actions, templates, notifications):
        self.name = name
        self.template_dirs = template_dirs
        self.actions = {}
        self.templates = {}
        self.notification_types = {}

        for a in actions:
            self.actions[a['name']] = a

        for t in templates:
            self.templates[t['type']] = t

        logger.debug("%s", notifications)
        for n in notifications:
            logger.debug("concrete notif: %s", n)
            self.notification_types[n['name']] = n

        self.init_jinja_env()

    @classmethod
    def from_file(cls, filepath, templates_dir):
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Failed to open plugin file '%s'", filepath)
            return None
        except yaml.YAMLError:
            logger.warning("Failed to deserialize yaml file '%s'", filepath)
            return None

        if not cls.valid_schema(data):
            logger.warning("Failed to load plugin from file '%s' due to invalid YAML schema", f)
            return None

        # TODO: filter out extra unnecessary data
        # i.e. anything not needed for plugin that is present in yaml file

        path = pathlib.Path(filepath)
        filename = path.stem

        jinja_template_dirs = [
            os.path.join(templates_dir, filename),
            path.parent,
        ]
        return cls(filename, jinja_template_dirs, **data)

    @classmethod
    def valid_schema(cls, data):
        """Simple validation of plugin structure similar to YAML schema validation"""
        for key, values in cls.SCHEMA.items():
            if key not in data.keys():
                logger.warning("Mandatory section is missing: '%s'", key)
                return False

            data_vals = data[key]
            schema_val_set = set(values)

            for val in data_vals:
                # set comparisons between schema.values and data_vals.keys()
                diff = schema_val_set - set(val.keys())

                if diff:
                    logger.warning("Mandatory attributes are missing: %s", diff)
                    return False

        return True

    def init_jinja_env(self):
        template_loader = jinja2.FileSystemLoader(self.template_dirs)
        self.jinja_env = jinja2.Environment(
            loader=template_loader,
            autoescape=True,
            extensions=['jinja2.ext.i18n']
        )

    def get_actions(self):
        return self.actions

    def get_templates(self):
        return self.templates

    def get_notification_types(self):
        return self.notification_types

    def get_jinja_env(self):
        return self.jinja_env
