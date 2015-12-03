import Pyro4
from ui import ConfigParser
from time import sleep
from ui.arg_parser import init_config_from_argv
from multiprocessing import Process
from subprocess import Popen
from sys import argv
from os.path import isfile, join, dirname, abspath
import dispatcher as dis

NS_CMD = "pyro4-ns"


class BadUsage(Exception):
    pass


def send_command(host, i):
    print(host.run_slave())


def set_up_slaves(processes):
    init_config_from_argv()
    config = ConfigParser()
    hosts = config.build_hosts()

    for i, host in enumerate(hosts):
        p = Process(target=send_command, args=(host, i))
        p.start()
        processes.append(p)
    print("Launched all processes")


def check_ns_present():
    try:
        Pyro4.locateNS()
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
    try:
        Pyro4.Proxy("PYRONAME:%s" % dis.DISPATCHER_NAME)
    except AttributeError:
        return False
    else:
        return True


def print_usage():
    print("Usage: ./launcher config_file.yml")

if __name__ == "__main__":
    try:
        config_file = get_config_file()
    except BadUsage:
        print_usage()
        exit(-1)

    try:
        if not check_ns_present():
            # launch ns
            ns_p = Popen([NS_CMD])
            print("NS launched.")

            # check the ns is correctly set up
            while not check_ns_present():
                print("Unable to locate NS, waiting it to set up. Sleeping 1s.")
                sleep(1)

        print("NS launched and located.")

        # launch dispatcher
        disp_p = Popen(["/usr/bin/python3.4",
                        join(dirname(abspath(__file__)), "dispatcher.py"),
                        config_file])

        while not check_dispatcher_present():
            if disp_p.poll():
                print("Error in dispatcher. Aborting")
                exit(-1)
            print("Dispatcher not ready, sleeping 1s.")
            sleep(1)

        print("Dispatcher ready. Launching slaves.")

        processes = []
        set_up_slaves(processes)
        for proc in processes:
            proc.join()
        print("Done all processes")

        disp_p.kill()

    finally:
        if ns_p:
            ns_p.kill()
