from file_transfer import Host
from ui import ConfigParser
import logging
from ui.arg_parser import init_config_from_argv
from multiprocessing import Process

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("paramiko").setLevel(logging.CRITICAL)


def send_command(host, i):
    print(host.send_ssh_command("sleep file%i.txt" % i)[0])

if __name__ == "__main__":
    init_config_from_argv()
    config = ConfigParser()
    hosts = config.build_hosts()
    processes = []
    for i, host in enumerate(hosts):
        p = Process(target=send_command, args=(host, i))
        p.start()
        processes.append(p)
    print("Launched all processes")
    for proc in processes:
        proc.join()
    print("Done all processes")