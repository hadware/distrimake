from file_transfer import Host
from ui import ConfigParser

if __name__ == "__main__":
    config = ConfigParser("configs/teamdata.yaml")
    test_host = config.build_hosts()[0]
    print(test_host.send_ssh_command("ls")[1].read())
    print("ok")