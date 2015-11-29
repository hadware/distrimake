from file_transfer import Host
from ui import ConfigParser
import logging
from ui.arg_parser import init_config_from_argv

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("paramiko").setLevel(logging.CRITICAL)

if __name__ == "__main__":
    init_config_from_argv()
    config = ConfigParser()
    test_host = config.build_hosts()[0]
    print(test_host.send_ssh_command("ls testpyro")[0])
    test_host.deploy_remote_venv()
    test_host.run_slave()
    print("ok")
    test_host.disconnect()