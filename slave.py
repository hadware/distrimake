from datetime import datetime
from sys import executable
import logging
import sys
from time import sleep
import Pyro4.core
import subprocess
from exceptions import NoJobAvailableYet, AllJobsCompleted

DISPATCHER_NAME = 'distrimake.dispatcher'


class Slave:
    def __init__(self, name):
        self.name = name
        self.dispatcher = Pyro4.Proxy("PYRONAME:%s" % DISPATCHER_NAME)
        logging.debug("Dispatcher acquired")

    def run(self):
        while True:
            try:
                job = self.dispatcher.get_work()
            except NoJobAvailableYet:
                sleep(2)
            except AllJobsCompleted:
                logging.debug("All work completed, exiting.")
                break
            else:
                self._execute_job(job)

    def _execute_job(self, job):
        logging.debug("Handling job : '%s'" % job.__str__())
        logging.debug("Getting files : [%s]" % ', '.join(job.dependency_filepaths))
        self.dispatcher.request_file(job.dependency_filepaths, self.name)
        try:
            logging.debug("Executing job : %s" % '; '.join(job.rule.commands))
            job.execute()
        except subprocess.CalledProcessError as e:
            logging.error(e.output)
        else:
            logging.debug("Uploading target : %s" % job.rule.target)
            self.dispatcher.upload_file(job.rule.target)


if __name__ == "__main__":
    if len(sys.argv) < 1:
        exit(-1)

    name = sys.argv[1]
    logging.basicConfig(filename=("%s.log" % name), level=logging.DEBUG)
    print(AllJobsCompleted.__module__)
    worker = Slave(name)
    worker.run()

