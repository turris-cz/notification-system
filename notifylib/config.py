import configparser


def load_config(filename):
    config.read(filename)


def default_config():
    conf = configparser.ConfigParser()
    conf.add_section("settings")
    conf.set("settings", "volatile_dir", "/tmp")
    conf.set("settings", "persistent_dir", "/srv")
    conf.set("settings", "plugin_dir", "plugins")
    conf.set("settings", "logfile", "notifylib.log")

    return conf


config = default_config()
