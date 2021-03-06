from sys import argv

import Pyro4

import syntax_tree as st
from parser import parse_makefile
from ui import ConfigParser
from daemons import DISPATCHER_NAME, NoJobAvailableYet, AllJobsCompleted

class Dispatcher(object):
    def __init__(self, config_file):
        config = ConfigParser(config_file)

        # init scheduler for task list
        makefile = parse_makefile(config.mkfile_filepath)
        self.scheduler = makefile.build_deps(config.mk_target)

        self.map_host = {}
        for host in config.build_hosts():
            self.map_host[host.name] = host

    def get_work(self):
        try:
            job = self.scheduler.get_job()
        except st.AllJobsCompleted:
            raise AllJobsCompleted()
        except st.HigherLevelJobsStillRunning:
            raise NoJobAvailableYet()
        else:
            return job

    def put_result(self, job):
        try:
            self.scheduler.finish_job(job)
        except st.JobAlreadyDone:
            pass

    def request_file(self, file_names, slave_name):
        """Tells the dispatcher to send over files needed to complete the job"""
        self.map_host[slave_name].send_files(file_names)

    def upload_file(self, file_names, slave_name, local_path=None):
        """Tells the dispatcher to retrieve the target file after the job is done"""
        self.map_host[slave_name].get_files(file_names, local_folder=local_path)


# main program
def main_dispatcher():

    Pyro4.config.SERIALIZER = 'pickle'
    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']

    if len(argv) != 3:
        print("Not enough args")
        exit(-1)

    print(argv[2])
    ns = Pyro4.naming.locateNS(host=argv[2])

    dispatcher = Dispatcher(argv[1])
    Pyro4.config.HOST = argv[2]
    daemon = Pyro4.core.Daemon()
    uri = daemon.register(dispatcher)
    ns.register(DISPATCHER_NAME, uri)

    print("Dispatcher initialised and registered.")
    print(AllJobsCompleted.__module__)
    daemon.requestLoop()

if __name__ == '__main__':

    main_dispatcher()
