import configparser


class Config:
    def __init__(self):
        self.default_config()

    def default_config(self):
        self.conf = configparser.ConfigParser()
        self.conf.add_section("settings")
        self.conf.set("settings", "volatile_dir", "/tmp")
        self.conf.set("settings", "persistent_dir", "/srv")
        self.conf.set("settings", "plugin_dir", "plugins")
        self.conf.set("settings", "templates_dir", "templates")
        self.conf.set("settings", "logfile", "notifylib.log")

    def load_config(self, filename):
        self.conf.read_file(open(filename))

    def get(self, section, key):
        return self.conf.get(section, key)


config = Config()
