from os.path import isfile, join, getctime


class SchedulerException(Exception):
    pass

class NothingToBeDone(SchedulerException):
    pass

class AllJobsCompleted(SchedulerException):
    pass

class JobAlreadyDone(SchedulerException):
    pass

class Job:
    """Stores everything the master process needs to assign jobs to slaves processes:
    - The rule (with the commands to be ran)
    - The dependency filepaths, so the master process know which files to send to the
    slave processes"""

    def __init__(self, rule, order):
        self.rule = rule
        self.level = order
        self.dependency_filepaths = None # filled when the job is "getted"

    def create_file_deps(self, makefile_folder):
        self.dependency_filepaths = [join(makefile_folder, dep.name)
                                     for dep in [self.rule.dependencies]
                                     if isfile(join(makefile_folder, dep.name))]

class Scheduler():

    def __init__(self, rule_table, target_symbol, makefile_folder):
        self.rule_table = rule_table
        self.makefile_folder = makefile_folder

        # both job lbl and tbl set during the build deps call
        self.pending_job_lvl = None
        self.pending_jobs_tbl = dict()
        self._build_dep(target_symbol)

        # used afterward to store jobs taken by the master process
        self.running_jobs = []


    def _check_if_tg_required(self, tg_symbol):
        """Checks if the rule associated with tg_symbol should be ran or not. It's true if:
        - The target isn't an existing file (then it's a rule, or a file that needs to be created)
        - One of the rule's dependencies isn't a file
        - One of the rule's dependency isn't a file, and has a more recent timestamp
        """

        # checking if it's a file
        tg_filepath = join(self.makefile_folder, tg_symbol.name)
        if not isfile(tg_filepath):
            return True

        # checking the dependency
        for dependency in self.rule_table[tg_symbol].dependencies:
            dep_filepath = join(self.makefile_folder, dependency.name)

            if isfile(join(self.makefile_folder, dependency.name)):
                # dep have a more recent timestamp than tgt
                if getctime(dep_filepath) > getctime(tg_filepath): # checking the timestamp
                    return True
            else:
                return True

        return False

    def _create_job(self, tg_symbol, job_level):
        """Adds the job the the pending job table, checking beforehand that
        the symbol isn't just a required file and not a rule's target"""
        if tg_symbol in self.rule_table:
            self.pending_jobs_tbl[job_level].append(Job(self.rule_table[tg_symbol],
                                                        job_level))

    def _build_dep(self, symbol):
        """Takes a symbol as an input, which corresponds to a rule, and
        builds the jobs table for that rule"""

        #iterative algorithm, recusive is cool, but we're engineers not researchers

        if self._check_if_tg_required(symbol): #init with the make target
            self.pending_jobs_tbl[0] = Job(self.rule_table[symbol], 0)
        else:
            raise NothingToBeDone()

        found_new_deps_flag = True #used to know if we should keep going
        current_job_lvl = 0

        while found_new_deps_flag:
            found_new_deps_flag = False # Has to be raised for the next iteration of the look to run
            self.pending_jobs_tbl[current_job_lvl + 1] = []

            for job in self .pending_jobs_tbl[current_job_lvl]:
                for dep_symbol in job.rule.dependencies:
                    if self._check_if_tg_required(dep_symbol):
                        self._create_job(dep_symbol, current_job_lvl + 1)
                        found_new_deps_flag = True

            current_job_lvl += 1

        self.pending_job_lvl = current_job_lvl - 1 # compensating for the extra + 1


    def get_job(self):
        """Called by the master to retrieve a job from the scheduler.
        Retrieves a job from the job table, puts it in the running job list,
        and returns it"""
        if not self.pending_jobs_tbl[self.pending_job_lvl]:
            self.pending_job_lvl -= 1
        if self.pending_job_lvl == -1:
            raise AllJobsCompleted()

        job = self.pending_jobs_tbl[self.pending_job_lvl].pop()
        job.create_file_deps(self.makefile_folder)
        self.running_jobs.append(job)
        return job

    def finish_job(self, finished_job):
        """Called by the master when a job has terminated. Tells the
        scheduler that the job has been finished"""
        if finished_job in self.running_jobs:
            self.running_jobs.remove(finished_job)
        else:
            raise JobAlreadyDone()
