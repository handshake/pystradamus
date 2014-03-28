import logging
import sys

def format_timedelta(dt):
    """Formats a datetime.timedelta into a simple string of days, hours, minutes
    and seconds
    """
    ts = dt.total_seconds()
    days, r = divmod(ts, 84600)
    hours, r = divmod(r, 3600)
    minutes, r = divmod(r, 60)
    return "%dD %02d:%02d:%02f" % (days, hours, minutes, r)

def error_exit(message, exit_code=1):
    """Bail out with an exit code
    """
    logging.error(message)
    sys.exit(exit_code)
