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

class SSHCredentials:

    class CredentialsType(Enum):
        KEY = 1
        PASSWORD = 2

    def __init__(self, cred_type, *args):
        self.cred_type = cred_type
        try:
            if cred_type == self.CredentialsType.KEY:
                self.key_path = args[0]
            else:
                self.login, self.password = args[0], args[1]
        except:
            MissingCredentials()

class RemoteConnection:

    class Status(Enum):
        DISCONNECTED = 1
        CONNECTION = 2

    def __init__(self, credentials, domain):
        self.status = self.Status.DISCONNECTED
        self.credentials = credentials
        self.domain = domain

    def connect(self):
        pass

    def disconnect(self):
        pass

class SFTPConnection(RemoteConnection):

    def __init__(self, credentials, domain):
        super().__init__(credentials, domain)
        self.connection = None

class SSHConnection(RemoteConnection):

    def __init__(self, credentials, domain):
        super().__init__(credentials, domain)
        self.connection = None

class Host:

    def __init__(self, **kwargs):

        if kwargs.get("key"):
            self.credentials = SSHCredentials(SSHCredentials.CredentialsType.KEY, kwargs.get("key"))
        elif kwargs.get("login") and kwargs.get("password"):
            self.credentials = SSHCredentials(SSHCredentials.CredentialsType.KEY,
                                              kwargs.get("login"),
                                              kwargs.get("password"))
        else:
            raise MissingCredentials()

        self.remote_location = kwargs.get("remote_location", "")

        try:
            self.domain = kwargs["domain"]
        except KeyError:
            raise MissingDomain()

        self.sftp_conection = SFTPConnection(self.credentials, self.domain)
        self.ssh_connection = SSHConnection(self.credentials, self.domain)

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
