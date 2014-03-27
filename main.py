#!/usr/bin/env python
import argparse
import datetime
import requests
from pprint import pprint

from dateutil.parser import parse as date_parse

JIRA_URL = "https://jira.handshake-app.com"
JIRA_USERNAME = "jirabot"
JIRA_PASSWORD = "jirabot"
IN_PROGRESS_ID = 3
ESTIMATE_FIELD_ID = "customfield_10102"

#BENEFIT_SIZE_ID = "customfield_10601"
#EFFORT_SIZE_ID = "customfield_10600"

class JIRA(object):

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def get(self, url, params=None, extra_headers=None):
        headers = {'Content-Type': 'application/json'}
        if extra_headers:
            headers.update(extra_headers)

        actual_url = "%s/rest/api/2/%s" % (self.base_url, url)
        print "getting %s" % actual_url,
        r = requests.get(actual_url, auth=(self.username, self.password),
                params=params, headers=headers)
        if r.status_code in (200,):
            print "[ OK ]"
            #print r.json()
            return r.json()
        else:
            print "[FAIL]"
            raise RuntimeError(r.text)

    def pull_history(self, user, limit=25):
        print "pulling history"
        offset = 0
        fetched = 0
        total = 2**31
        issues = []
        while len(issues) < total:
            resp = self.get('search', params={
                'jql': 'assignee = %s AND status in (Closed, "In Review", Merged) ORDER BY updated DESC' % user,
                'fields': '%s,summary' % ESTIMATE_FIELD_ID,
                'expand': 'changelog',
                'startAt': offset,
                'maxResults': limit
              })
            total = resp['total']
            issues += resp['issues']
            offset += limit
        print "received %d issues" % len(issues)

        for i in issues:
            estimate = i['fields'].get(ESTIMATE_FIELD_ID)
            # stroll through the history
            raw_history = i.get('changelog', {}).get('histories', [])
            time_spent_in_progress = datetime.timedelta()
            start_time = None
            end_time = None
            for idx, h in enumerate(raw_history):
                for item in h['items']:
                    if item['field'] == 'status':
                        when = date_parse(h['created'])
                        if item['toString'] == 'In Progress':
                            start_time = when
                        if item['fromString'] == 'In Progress':
                            end_time = when
            if start_time and end_time:
                time_spent_in_progress = end_time - start_time
            if estimate and time_spent_in_progress:
                print "%s ESTIMATED: %s ELAPSED: %s" % (
                        i['key'], estimate,
                        format_timedelta(time_spent_in_progress))
            #pprint(i)

def format_timedelta(dt):
    ts = dt.total_seconds()
    days, r = divmod(ts, 84600)
    hours, r = divmod(r, 3600)
    minutes, r = divmod(r, 60)
    return "%dD %02d:%02d:%02f" % (days, hours, minutes, r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('username', type=str, help='JIRA username to query tickets for')
    args = parser.parse_args()

    j = JIRA(JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD)
    j.pull_history(args.username, 500)
