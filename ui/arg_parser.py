"""The Command line bash parser that reads all user args to build a complete config object"""
from sys import argv
from os.path import isfile

from ui import ConfigParser


def init_config_from_argv():

    def check_config_file(filepath):
        if isfile(filepath):
            config = ConfigParser(filepath)
        else:
            exit("Configuration file not found")
    if len(argv) == 2:
        check_config_file(argv[1])

    elif len(argv) == 3:
        check_config_file(argv[2])

    else:
        exit("Usage: ./distrimake.py config_file.yaml")
