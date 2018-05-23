import configparser
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def load_config(filename):
    try:
        config.read_file(open(filename, 'r'))
    except Exception as e:
        print("Failed to load config file, keeping original configuration")
        print(e)


config = configparser.ConfigParser()

# load default config
load_config(os.path.join(BASE_PATH, "config.conf"))
