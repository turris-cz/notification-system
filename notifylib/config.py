import configparser
import logging
import os.path

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.module_path = os.path.dirname(os.path.abspath(__file__))
        self.default_config()

    def default_config(self):
        self.conf = configparser.ConfigParser()
        self.conf.add_section("settings")
        self.conf.set("settings", "volatile_dir", "/tmp")
        self.conf.set("settings", "persistent_dir", "/srv")
        self.conf.set("settings", "plugin_dir", os.path.join(self.module_path, 'plugins'))
        self.conf.set("settings", "cmd_timeout", "10")

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                self.conf.read_file(f)
        except FileNotFoundError:
            logger.warning("Failed to open config file '{}'".format(filename))
        # TODO: handle configparser exceptions

    def load_from_dict(self, dictionary):
        self.conf.read_dict(dictionary)

    def get(self, section, key):
        return self.conf.get(section, key)

    def getint(self, section, key):
        return self.conf.getint(section, key)


config = Config()
