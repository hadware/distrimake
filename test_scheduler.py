from parser import parse_makefile
from syntax_tree import MakeFile

if __name__ == "__main__":
    print("Task dependency tree testing \n\n")
    mkfile_tree = parse_makefile("examples/very_simple_makefile")
    mkfile_tree.build_deps("all")
    print(mkfile_tree.scheduler.print_pending_jobs())

    mkfile_tree = parse_makefile("examples/premier/Makefile")
    mkfile_tree.build_deps("list.txt")
    print(mkfile_tree.scheduler.print_pending_jobs())

    mkfile_tree = parse_makefile("examples/blender_2.59/Makefile")
    mkfile_tree.build_deps("out.avi")
    print(mkfile_tree.scheduler.print_pending_jobs())

    print("Job scheduling testing \n\n")
    jobs = [mkfile_tree.scheduler.get_job() for i in range(100)] # gettin' jobs
    print(mkfile_tree.scheduler.print_running_jobs()) # printing the running jobs
    for job in jobs:
        mkfile_tree.scheduler.finish_job(job) # finishin' jobs
    print(mkfile_tree.scheduler.print_running_jobs()) # printin' again, should be empty
    print(mkfile_tree.scheduler.print_pending_jobs()) # there should be less jobs in there

