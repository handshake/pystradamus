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

    def get_estimated_tickets_for_user(self, username, limit=10):
        """Finds the next `limit` tickets for a given user that are estimated,
        assigned and in a "newish" status. They come back in backlog rank order.
        """
        log.debug("fetching next ticket for %s", username)

        jql = ' '.join([
            'assignee = %s' % username,
            'AND cf[%s] is not EMPTY' % self.estimate_field_id,
            'AND status in (New, "On Deck")',
            'AND resolution is EMPTY',
            'ORDER BY rank ASC'
        ])
        resp = self.get('search', params={
            'jql': jql,
            #'fields': 'all',
            'startAt': 0,
            'maxResults': limit
          })
        log.debug("found %d tickets", resp['total'])

        tickets = []
        # break these into more digestible python dicts so the other parts of
        # the system don't need to know about Jira's internal format
        for i in resp['issues']:
            tickets.append({
                "key": i['key'],
                "summary": i['fields']['summary'],
                "estimate": i['fields']['customfield_%s' % \
                        self.estimate_field_id]
                })

        return tickets

    def get_custom_fields(self):
        """Pulls the custom fields and their internal ids. Mostly useful when
        you have the url+auth for a Jira server but none of the needed internal
        ids
        """
        customs = []
        for f in self.get('field'):
            if f['custom']:
                customs.append({
                    'name': f['name'],
                    'id': f['id']
                    })
        return customs

