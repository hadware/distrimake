from enum import Enum
from os.path import isfile, join, realpath
from paramiko import AutoAddPolicy, SSHClient
from pysftp import Connection

"""This module describes the host class, which handles remote SSH commands and SFTP file transfers to
the slave host"""

VENV_ACTIVATE_COMMAND = "pyvenv venv"
PYRO_SLAVE_RUN_COMMAND = ""
VENV_SETUP_COMMANDS=[
    VENV_ACTIVATE_COMMAND,
    "source venv/bin/activate"
    "pip3 install pyro4",
    PYRO_SLAVE_RUN_COMMAND
]


class FileTransferError(Exception):
    pass

class MissingCredentials(FileTransferError):
    pass

class MissingDomain(FileTransferError):
    pass

class FailingConnection(FileTransferError):
    pass

class SSHCredentials:

    class CredentialsType(Enum):
        KEY = 1
        PASSWORD = 2

    def __init__(self, cred_type, login, *args):
        self.cred_type = cred_type
        self.login = login
        if cred_type == self.CredentialsType.KEY:
            self.key_path = args[0]
            if not isfile(self.key_path):
                raise MissingCredentials("SSH key path doesn't point to an existing key file")
        else:
            self.password = args[0]

class ConnectionType(Enum):
    SSH = 1
    SFTP = 2

class RemoteConnection:

    class Status(Enum):
        DISCONNECTED = 1
        CONNECTED = 2

    def __init__(self, credentials, domain):
        self.status = self.Status.DISCONNECTED
        self.credentials = credentials
        self.domain = domain
        self.client = None

    def connect(self):
        pass

    def disconnect(self):
        try:
            self.client.close()
        except:
            pass
        self.status = self.Status.DISCONNECTED

class SFTPConnection(RemoteConnection):

    def __init__(self, credentials, domain):
        super().__init__(credentials, domain)

    def connect(self):
        try:
            if self.credentials.cred_type == SSHCredentials.CredentialsType.KEY:
                self.client = Connection(self.domain, username=self.credentials.login,
                                         private_key=self.credentials.key)
            else:
                self.client = Connection(self.domain, username=self.credentials.login,
                                         password=self.credentials.password)
        except:
            FailingConnection("SFTP connection failing")
        finally:
            self.status = self.Status.CONNECTED


class SSHConnection(RemoteConnection):

    def __init__(self, credentials, domain):
        super().__init__(credentials, domain)
        self.client = self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def connect(self):
        try:
            if self.credentials.cred_type == SSHCredentials.CredentialsType.KEY:
                self.client.connect(self.domain, username=self.credentials.login,
                                    key_filename=self.credentials.key)
            else:
                self.client.connect(self.domain, username=self.credentials.login,
                                    password=self.credentials.password)
        except:
            FailingConnection("SSH connection failing")
        finally:
            self.status = self.Status.CONNECTED


def needs_connection(type):
    """Decorating function that checks if the sftp connection has been opened before the decorated function runs
    If it hasn't, it'll open it beforehand"""
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            if type == ConnectionType.SSH:
                if args[0].ssh_connection.status == SSHConnection.Status.DISCONNECTED:
                    args[0].ssh_connection.connect()
            else:
                if args[0].sftp_connection.status == SFTPConnection.Status.DISCONNECTED:
                    args[0].sftp_connection.connect()
            return func(*args, **kwargs)
        return inner_wrapper
    return wrapper

class Host:

    def __init__(self, name, **kwargs):

        if kwargs.get("login"):
            if kwargs.get("key"):
                self.credentials = SSHCredentials(SSHCredentials.CredentialsType.KEY,
                                                  kwargs.get("login"),
                                                  kwargs.get("key"))
            elif kwargs.get("password"):
                self.credentials = SSHCredentials(SSHCredentials.CredentialsType.PASSWORD,
                                                  kwargs.get("login"),
                                                  kwargs.get("password"))
            else:
               raise MissingCredentials("Can't find password or key in the host config file for host %s" % name)
        else:
            raise MissingCredentials("Can't find username in the host config file for host %s" % name)

        self.remote_location = kwargs.get("remote_location", "")

        try:
            self.domain = kwargs["domain"]
        except KeyError:
            raise MissingDomain("Can't find the domain or ip address in the host config file for host %s" % name)

        self.sftp_connection = SFTPConnection(self.credentials, self.domain)
        self.ssh_connection = SSHConnection(self.credentials, self.domain)

    @needs_connection(ConnectionType.SFTP)
    def send_files(self, files_list):
        if not isinstance(files_list, list):
            # could be just a single file, let's change that
            files = [files_list]
        else:
            files = files_list

        for file in files:
            self.sftp_connection.client.put(join(self.remote_location, file))

    @needs_connection(ConnectionType.SSH)
    def send_ssh_command(self, ssh_command):
        """Sends a SSH command to the host"""
        return self.ssh_connection.client.exec_command(ssh_command)

    @needs_connection(ConnectionType.SFTP)
    def check_venv_setup(self):
        """Checks if all the file needed for the venv are there"""
        return self.sftp_connection.client.isfile(join(self.remote_location, "venv/bin/activate")) and \
               self.sftp_connection.client.isfile(join(self.remote_location, "venv/bin/pyro4-ns"))

    @needs_connection(ConnectionType.SFTP)
    @needs_connection(ConnectionType.SSH)
    def deploy_remote_venv(self):
        """Sets up the venv needed to run the makefile"""
        self.send_ssh_command("cd %s" % self.remote_location)
        if self.check_venv_setup():
            self.send_ssh_command(VENV_ACTIVATE_COMMAND)
            self.send_ssh_command(PYRO_SLAVE_RUN_COMMAND)
        else:
            for command in VENV_SETUP_COMMANDS:
                self.send_ssh_command(command)
        #this is done to find the real local path of the slave name
        slave_path = join(dirname(__file__), "slave.py")
        self.send_files(slave_path)
        # TODO : Deploy the needed additionary files