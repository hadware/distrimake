
class DispatcherException(Exception):
    pass


class NoJobAvailableYet(DispatcherException):
    pass


class AllJobsCompleted(DispatcherException):
    pass
