import datetime
import logging
import pprint
from collections import defaultdict

from dateutil.parser import parse as date_parse

from .jira import (Jira, JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD,
        ESTIMATE_FIELD_ID)
from .utils import format_timedelta

log = logging.getLogger(__name__)

def accumulate_time_in_status(histories):
    """Given a dict of Jira "histories" find the ones that represent changes to
    ticket status, and accumulate the calendar time a ticket spent in a
    particular status. The time is cummulative.
    """
    #issue = "HS-1928"
    accumulator = datetime.timedelta()
    starts = []
    ends = []
    for h in histories:
        for item in h['items']:
            if item['field'] == 'status':
                if item['fromString'] == 'In Progress':
                    ends.append(date_parse(h['created']))
                elif item['toString'] == 'In Progress':
                    starts.append(date_parse(h['created']))
                    #print item['fromString'], '->', item['toString']
    for start, stop in zip(starts, ends):
        accumulator += (stop - start)
    return accumulator

def main(args):
    log.debug("HISTORY! %s", args)

    # for when config objects work
    #j = Jira.from_config(args.config)
    j = Jira(JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD)

    log.debug("pulling history")

    offset = 0
    limit = 200
    fetched = 0
    total = 2**31
    issues = []
    while len(issues) < total:
        resp = j.get('search', params={
            'jql': 'assignee = %s AND status = Closed AND resolution = Done '\
                    'ORDER BY updated DESC' % args.username,
            'fields': '%s,summary' % ESTIMATE_FIELD_ID,
            'expand': 'changelog',
            'startAt': offset,
            'maxResults': limit
          })
        total = resp['total']
        issues += resp['issues']
        offset += limit
    log.debug("received %d issues", len(issues))

    estimates = defaultdict(list)

    for i in issues:
        estimate = i['fields'].get(ESTIMATE_FIELD_ID)
        # stroll through the history
        raw_history = i.get('changelog', {}).get('histories', [])
        time_spent_in_progress = accumulate_time_in_status(raw_history)
        if estimate and time_spent_in_progress:
            estimates[estimate].append(time_spent_in_progress)
            #log.info("%s ESTIMATE: %s ELAPSED: %s", i['key'], estimate,
            #        time_spent_in_progress.total_seconds())
            #log.debug("%s ESTIMATED: %s ELAPSED: %s", i['key'], estimate,
            #        format_timedelta(time_spent_in_progress))

    for estimate in sorted(estimates.keys(), reverse=True):
        print "*" * 80
        print "ESTIMATE: %s" % estimate
        for t in sorted(estimates[estimate], reverse=True):
            #print t.total_seconds()
            print format_timedelta(t)

