from pymongo import MongoClient
from jira.client import JIRA

import os
import logging

from dateutil.parser import parse

JIRA_SERVER = os.environ.get('JIRA_SERVER')
JIRA_CRED = os.environ.get('JIRA_CRED')

if not JIRA_SERVER or not JIRA_CRED:
    raise ValueError(
        "JIRA_SERVER and JIRA_CRED environment variables required")


log = logging.getLogger("jira.sync")


def transform(i):
    d = {}
    d["_id"] = i.id
    d["name"] = i.key
    d["url"] = i.self
    d["summary"] = i.fields.summary
    d["description"] = i.fields.description
    d['labels'] = i.fields.labels
    # Sigh.. cause issues with comparison due to lose of tz with mongo.
    d['created'] = parse(i.fields.created).replace(tzinfo=None)
    if i.fields.assignee:
        d['assignee'] = i.fields.assignee.displayName
    d['type'] = i.fields.issuetype.name
    if i.fields.resolution:
        d['resolution'] = i.fields.resolution.name
    if i.fields.status:
        d['status'] = i.fields.status.name
    if i.fields.duedate:
        d['duedate'] = parse(i.fields.duedate)

    env = i.fields.environment
    if env:
        if ',' in env:
            sites = [s.strip() for s in env.split(",")]
        if ":" in env:
            sites = [s.strip() for s in env.split(":")]
        if ";" in env:
            sites = [s.strip() for s in env.split(";")]
        else:
            sites = [env]
        d['sites'] = sites
    return d


def main():
    logging.basicConfig(level=logging.DEBUG)

    client = MongoClient()
    db = client.zephyr
    user, password = JIRA_CRED.split(":", 1)
    options = {'server': JIRA_SERVER}

    jira = JIRA(basic_auth=(user, password), options=options)

    issues = jira.search_issues('project=CM', maxResults=100)
    for i in issues:
        d = transform(i)
        i_db = db.cm_issues.find_one({"_id": i.id})

        if i_db is not None:
            if i_db != d:
                log.debug("Updating issue %s" % i.key)
            else:
                continue
        else:
            log.debug("Syncing issue %s" % i.key)

        db.cm_issues.update({"_id": i.id}, d, upsert=True)


if __name__ == '__main__':
    try:
        main()
    except:
       import pdb, traceback, sys
       traceback.print_exc()
       pdb.post_mortem(sys.exc_info()[-1])
