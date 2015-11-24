import yaml

""""The YAML config parser and singleton class, reachable by any object needing it"""


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):

    def __init__(self, config_file_path):
        pass