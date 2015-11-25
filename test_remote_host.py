from file_transfer import Host
from ui import ConfigParser
import logging

logging.getLogger().setLevel(logging.DEBUG)

if __name__ == "__main__":
    config = ConfigParser("configs/teamdata.yaml")
    test_host = config.build_hosts()[0]
    print(test_host.send_ssh_command("rm LICENSE")[0])
    test_host.send_files("LICENSE")
    print(test_host.send_ssh_command("ls")[0])
    test_host.deploy_remote_venv()
    test_host.run_slave()
    print("ok")