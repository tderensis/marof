from time import mktime
from datetime import datetime
"""
Contains timing functions that are useful for timestamps.
"""

def getMicroSeconds():
    """ Gets the time in microseconds since the epoch in UTC.
    
    :returns microseconds since the epoch in UTC as a long
    """
    now = datetime.utcnow()
    return long((mktime(now.timetuple()) + 1e-6*now.microsecond)*1e6)

def getSeconds():
    """ Gets the time in seconds since the epoch in UTC.
    
    :returns seconds since the epoch in UTC as a long
    """
    return long(mktime(datetime.utcnow().timetuple()))

def getMilliSeconds():
    """ Gets the time in seconds since the epoch in UTC.
    
    :returns seconds since the epoch in UTC as a long
    """
    now = datetime.utcnow()
    return long((mktime(now.timetuple()) + 1e-6*now.microsecond)*1e3)
    