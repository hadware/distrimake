import Pyro4
from Pyro4.errors import NamingError
from ui import ConfigParser
from time import sleep
from multiprocessing import Process
from subprocess import Popen
from sys import argv
from os.path import isfile, join, dirname, abspath
import dispatcher as dis
from os import environ
import file_transfer

NS_CMD = ["pyro4-ns", "-n"]

Pyro4.config.SERIALIZER = 'pickle'


class BadUsage(Exception):
    pass




def send_command(host, i, ns_hostname):
    host.deploy_remote_venv()
    stdout, stderr = (host.run_slave(ns_hostname))
    print("%d : --------- stderr --------------->" % i)
    print(stderr.decode("utf-8"))
    print("%d : --------- stdout --------------->" % i)
    print(stdout.decode("utf-8"))



def set_up_slaves(processes, config):
    hosts = config.build_hosts()

    for i, host in enumerate(hosts):
        p = Process(target=send_command, args=(host, i, master_ip))

        p.start()
        processes.append(p)
    print("Launched all processes")


def check_ns_present():
    try:
        Pyro4.locateNS(host=master_ip)
    except Pyro4.errors.NamingError:
        return False
    else:
        return True


def get_config_file():
    if len(argv) == 2:
        if isfile(argv[1]):
            return argv[1]
    raise BadUsage()


def check_dispatcher_present():
    ns = Pyro4.locateNS(host=master_ip)
    try:
        ns.lookup(dis.DISPATCHER_NAME)
    except NamingError:
        return False
    else:
        return True


def print_usage():
    print("Usage: ./launcher config_file.yml")

if __name__ == "__main__":
    try:
        config_file = get_config_file()
        config = ConfigParser(config_file)
        master_ip = config.config_data.get("master_ip")
        print(master_ip)
    except BadUsage:
        print_usage()
        exit(-1)

    ns_p = None
    try:
        if not check_ns_present():
            # launch ns
            env = environ.copy()
            env['PYRO_SERIALIZERS_ACCEPTED'] = "serpent,json,marshal,pickle"
            NS_CMD.append(master_ip)
            ns_p = Popen(NS_CMD, env=env)
            print("NS launched.")
            Pyro4.config.NS_HOST = master_ip

            # check the ns is correctly set up
            while not check_ns_present():
                print("Unable to locate NS, waiting it to set up. Sleeping 1s.")
                sleep(1)

        print("NS launched and located.")

        # launch dispatcher
        disp_p = Popen(["/usr/bin/python3",
                        join(dirname(abspath(__file__)), "dispatcher.py"),
                        config_file, master_ip])

        while not check_dispatcher_present():
            if disp_p.poll():
                print("Error in dispatcher. Aborting")
                exit(-1)
            print("Dispatcher not ready, sleeping 1s.")
            sleep(1)

        print("Dispatcher ready. Launching slaves.")

        processes = []
        set_up_slaves(processes, config)
        for proc in processes:
            proc.join()
        print("Done all processes")

        disp_p.kill()

    finally:
        if ns_p:
            ns_p.kill()
