import logging

import requests

log = logging.getLogger(__name__)

class Jira(object):

    @classmethod
    def from_config(klass, cfg):
        return klass(cfg.get('jira', 'base_url'), cfg.get('jira', 'username'),
                cfg.get('jira', 'password'),
                cfg.get('jira', 'estimate_field_id'))

    def __init__(self, base_url, username, password, estimate_field_id):
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        self.base_url = base_url
        self.username = username
        self.password = password
        self.estimate_field_id = estimate_field_id

    def get(self, url, params=None, extra_headers=None):
        log.debug("getting %s", url)
        headers = {'Content-Type': 'application/json'}
        if extra_headers:
            headers.update(extra_headers)

        actual_url = "%s/rest/api/2/%s" % (self.base_url, url)
        r = requests.get(actual_url, auth=(self.username, self.password),
                params=params, headers=headers)
        if r.status_code in (200,):
            return r.json()
        else:
            log.warn("[%s] %s", r.status_code, r.text)
            return {}

    def get_issue_history_by_JQL(self, jql):
        """Uses the passed in JQL against the search api and retreives the
        expanded histories of each match
        """
        log.debug("getting issue history with jql: %s", jql)
        issues = []
        offset = 0
        limit = 200
        total = 1
        while len(issues) < total:
            log.debug("fetching %d issues starting at %s", limit, offset)
            resp = self.get('search', params={
                'jql': jql,
                'fields': 'customfield_%s,summary' % self.estimate_field_id,
                'expand': 'changelog',
                'startAt': offset,
                'maxResults': limit
              })
            total = resp['total']
            issues.extend(resp['issues'])
            offset += limit
        log.debug("received %d issues", len(issues))
        return issues
