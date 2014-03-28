import logging

import requests

log = logging.getLogger(__name__)

JIRA_URL = "https://jira.handshake-app.com"
JIRA_USERNAME = "jirabot"
JIRA_PASSWORD = "jirabot"
ESTIMATE_FIELD_ID = "customfield_10102"
#IN_PROGRESS_ID = 3
#BENEFIT_SIZE_ID = "customfield_10601"
#EFFORT_SIZE_ID = "customfield_10600"

class Jira(object):

    #@classmethod
    #def from_config(klass, config):
    #    return klass(config.base_url, config.username, config.password)

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

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
            raise RuntimeError(r.text)
