from time import mktime
from datetime import datetime

def getMicroSeconds():
    """ Gets the time in microseconds since the epoch. Should be used as the universal timing
    function.
    """
    now = datetime.utcnow()
    return long((mktime(now.timetuple()) + 1e-6*now.microsecond)*1e6)

def getSeconds():
    now = datetime.utcnow()
    return long(mktime(now.timetuple()))

def getMilliSeconds():
    now = datetime.utcnow()
    return long((mktime(now.timetuple()) + 1e-6*now.microsecond)*1e3)
    