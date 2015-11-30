from parser import parse_makefile
import sys
from os.path import isfile
from file_transfer import Host
from ui import ConfigParser
import logging
from syntax_tree import AllJobsCompleted, HigherLevelJobsStillRunning
import Pyro4

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("paramiko").setLevel(logging.CRITICAL)

class Master:

    def __init__(self, mkfile_filepath, target, hosts):
        self.makefile = parse_makefile(mkfile_filepath)
        self.makefile.build_deps(target)
        self.idle_slaves = []
        self.map_slave_job = map()
        self.hosts = hosts

        self._no_more_job = False


    def register_slave(self, slave):
        self.idle_slaves.append(slave)
        self._assign_job()

    def on_job_terminate(self, slave):
        if slave in self.map_slave_job:
            job = self.map_slave_job[slave]
            self.makefile.scheduler.finish_job(job)

            del self.map_slave_job[slave]
            self.idle_slaves.append(slave)

            self._assign_job()
        else:
            # TODO internal
            raise Exception()


    def _assign_job(self):
        if not self._no_more_job:
            for slave in self.idle_slaves:
                try:
                    job = self.makefile.scheduler.get_job()
                except HigherLevelJobsStillRunning:
                    break
                except AllJobsCompleted:
                    self._no_more_job = True
                    break

                self.idle_slaves.remove(slave)
                self.map_slave_job[slave] = job
                slave.launch_job(job)
        else:
            for slave in self.idle_slaves:
                slave.terminate()

            if not self.map_slave_job:
                self._work_complete()

    def _work_complete(self):
        for shost in self.hosts:
            shost.disconnect()

        exit(0)



if __name__ == "__main__":
    config = ConfigParser(sys.argv[0])

    hosts = config.build_hosts()
    #print(test_host.send_ssh_command("ls testpyro")[0])
    for host in hosts:
        host.deploy_remote_venv()
        host.run_slave()

    master = Master(config.mkfile_filepath, config.mk_target, hosts)

    Pyro4.core.initServer()
    daemon = Pyro4.core.Daemon()
    nameserver = Pyro4.locateNS()
    daemon.useNameServer(nameserver)

    uri = daemon.connect(master, "master")

    daemon.requestLoop()






