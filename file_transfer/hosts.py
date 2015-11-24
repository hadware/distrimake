from enum import Enum

from pysftp import Connection

"""This module describes the host class, which handles remote SSH commands and SFTP file transfers to
the slave host"""

class FileTransferError(Exception):
    pass

class MissingCredentials(FileTransferError):
    pass

class MissingDomain(FileTransferError):
    pass

class HostConnectionStatus(Enum):
    DISCONNECTED = 1
    CONNECTION = 2

class Host:

    def __init__(self, **kwargs):

        if kwargs.get("key"):
            pass
        elif kwargs.get("login") and kwargs.get("password"):
            pass
        else:
            raise MissingCredentials()

        self.remote_location = kwargs.getget("domain", "")

        try:
            self.domain = kwargs["domain"]
        except KeyError:
            raise MissingDomain()

        self.sftp_connection_status = HostConnectionStatus.DISCONNECTED
        self.sftp_connection = None
        self.ssh_connection_status = HostConnectionStatus.DISCONNECTED
        self.ssh_connection = None

    def sftp_connect(self):
        """Opens a SFTP connection with the remote host"""
        pass

    def ssh_connect(self):
        """Opens a SFTP connection with the remote host"""
        pass

    def send_files(self, files_list):
        if not isinstance(files_list, list):
            # could be just a single file, let's change that
            files = [files_list]
        else:
            files = files_list

        # TODO : Implement the actual file sending part

    def send_ssh_command(self, ssh_command):
        """Sends a SSH command to the host"""
        pass

    def deploy_remote_venv(self):
        """Sets up the venv needed to run the makefile"""
        pass
