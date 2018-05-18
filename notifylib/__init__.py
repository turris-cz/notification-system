import logging
import configparser
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# TODO: config loading at one place and import it elsewhere?
config = configparser.ConfigParser()
config.read(os.path.join(BASE_PATH, "config.conf"))

# TODO: logger config file

logger = logging.getLogger(config["logging"]["logger_name"])
# just use DEBUG level for now...
logger.setLevel(logging.DEBUG)

# log to file for now...
fh = logging.FileHandler("notifylib.log")
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

# TODO: log to syslog
