""""The YAML config parser and singleton class, reachable by any object needing it"""
from os.path import isfile, join, expanduser
import yaml

from file_transfer import Host, FileTransferError


class ConfigError(Exception):
    pass

class MissingIncludedFile(ConfigError):
    pass

class MissingHosts(ConfigError):
    pass

class WrongHostConfig(ConfigError):
    pass

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigParser(metaclass=Singleton):

    def __init__(self, config_file_path):
        with open(config_file_path, 'r') as config_file:
            self.config_data = yaml.load(config_file)

        self.mkfile_filepath = self.config_data.get("mkfile_path", "")
        self.distributed_run = self.config_data.get("distributed_run", True)
        self.included_files_list = self.config_data.get("included_files", [])
        if self.distributed_run and self.config_data.get("hosts") is None:
            raise MissingHosts("The hosts are missing in the config file")

    @property
    def included_files(self):
        for filename in self.included_files_list:
            if not isfile(join(self.mkfile_filepath, filename)):
                raise MissingIncludedFile("A listed included file cannot be found")

        return [join(self.mkfile_filepath, filename) for filename in self.included_files_list]

    def build_hosts(self):
        """Returns a list of hosts object, from the config file"""
        if self.distributed_run:
            hosts_list = list()
            for host_config in self.config_data["hosts"]:
                try :
                    host_name, host_config = host_config.popitem()
                    if host_config.get("key") and "~" in host_config["key"]:
                        host_config["key"] = expanduser(host_config["key"])
                    hosts_list.append(Host(host_name, **host_config))
                except KeyError:
                    raise WrongHostConfig()
                except FileTransferError as err:
                    raise err

            return hosts_list
        else:
            return None