import datetime
import logging
from collections import defaultdict

from dateutil.parser import parse as date_parse

from .jira import Jira
from .evidence import Evidence
from .storage import add_or_update_evidence
from .utils import format_timedelta, error_exit

log = logging.getLogger(__name__)

def main(args):
    """The command_line dispatches to this function whenever the `history`
    parser is matched. Do further dispatching here
    """
    if args.refresh:
        refresh(args)
    elif args.predict:
        predict(args)
    else:
        error_exit("%s requires either refresh or predict flags to be set." %
                __name__)

def accumulate_time_in_status(histories):
    """Given a dict of Jira "histories" find the ones that represent changes to
    ticket status, and accumulate the calendar time a ticket spent in a
    particular status. The time is cummulative.
    """
    accumulator = datetime.timedelta()
    starts = []
    ends = []
    for h in histories:
        for item in h['items']:
            if item['field'] == 'status':
                if item['toString'] == 'In Progress':
                    starts.append(date_parse(h['created']))
                elif item['fromString'] == 'In Progress':
                    ends.append(date_parse(h['created']))
    for start, stop in zip(starts, ends):
        accumulator += (stop - start)
    return accumulator

def refresh(args):
    """Main entry point of the history command. Builds jql to find closed issues
    for a given user.
    """
    log.debug("fetching history for user %s", args.username)

    j = Jira.from_config(args.cfg)
    jql = ' '.join([
        'assignee = %s AND' % args.username,
        'cf[%s] is not EMPTY AND' % j.estimate_field_id,
        'status = Closed AND',
        'resolution = Done',
        'ORDER BY updated DESC'
    ])
    issues = j.get_issue_history_by_JQL(jql)

    estimates = defaultdict(list)
    for i in issues:
        estimate = i['fields'].get("customfield_%s" % j.estimate_field_id)
        # stroll through the history
        raw_history = i.get('changelog', {}).get('histories', [])
        time_in_progress = accumulate_time_in_status(raw_history)
        if estimate and time_in_progress:
            estimates[estimate].append(time_in_progress)
            e = Evidence(i['key'], args.username, estimate, time_in_progress)
            add_or_update_evidence(e)

    for estimate in sorted(estimates.keys(), reverse=True):
        print "*" * 80
        print "ESTIMATE: %s" % estimate
        for t in sorted(estimates[estimate], reverse=True):
            #print t.total_seconds()
            print format_timedelta(t)

def predict(args):
    log.debug("predicting ticket completions for %s", args.username)

    j = Jira.from_config(args.cfg)
    tickets = j.get_estimated_tickets_for_user(args.username, limit=10)
    for t in tickets:
        print t
        #print t['key'], t['customfield_%s' % j.estimate_field_id]


