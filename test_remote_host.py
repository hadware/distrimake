from file_transfer import Host
from ui import ConfigParser
import logging
from ui.arg_parser import init_config_from_argv

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("paramiko").setLevel(logging.CRITICAL)

if __name__ == "__main__":
    init_config_from_argv()
    config = ConfigParser()
    test_host = config.build_hosts()
    # print(test_host[0].send_ssh_command("pwd")[0])
    for host in test_host:
        print(host.send_ssh_command("touch ahas.txt")[0])
        host.deploy_remote_venv()
        # host.run_slave()
    print("ok")
    for host in test_host:
        host.disconnect()