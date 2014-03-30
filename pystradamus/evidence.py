from .utils import format_timedelta

class Evidence(object):
    """A simple object that stores historic information for an estimated Jira
    ticket that is now completed
    """
    def __init__(self, ticket_id, username, estimate, elapsed_time):
        self.ticket_id = ticket_id
        self.username = username
        self.estimate = estimate
        self.elapsed_time = elapsed_time

    def __unicode__(self):
        return u'Estimate-%s [%s:%s] %s' % (self.ticket_id, self.estimate,
                self.username, format_timedelta(self.elapsed_time))
    __str__ = __unicode__
