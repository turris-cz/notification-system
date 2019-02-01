import logging
import pathlib

import yaml

logger = logging.getLogger(__name__)


class Plugin:
    SCHEMA = {
        'actions': ['name', 'title', 'command'],
        'templates': ['type', 'supported_media', 'src'],
    }
    # 'notifications' section is intentionally omitted for now
    # until mandatory and optional attributes check for 'notifications' is implemented

    def __init__(self, name, actions, templates, notifications):
        self.name = name
        self.actions = {}
        self.templates = {}
        self.notification_types = {}

        for a in actions:
            self.actions[a['name']] = a

        for t in templates:
            self.templates[t['type']] = t

        for n in notifications:
            self.notification_types[n['name']] = n

    @classmethod
    def from_file(cls, filepath):
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
        name = path.parent.stem

        return cls(name, **data)

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

    def get_actions(self):
        return self.actions

    def get_templates(self):
        return self.templates

    def get_notification_types(self):
        return self.notification_types

    def get_jinja_env(self):
        return self.jinja_env
