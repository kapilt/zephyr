import logging
import os

import github3
import pymongo

from controller import App

GH_CRED = os.environ.get("GITHUB_CRED")
GH_ORG = os.environ.get("GITHUB_ORG")

if not GH_CRED or not GH_ORG:
    raise ValueError("GITHUB_CRED and GITHUB_ORG env variables required")


def main():
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("github.relsync")

    user, password = GH_CRED.split(":", 1)
    gh = github3.login(user, password=password)
    client = pymongo.MongoClient()
    org = gh.organization(GH_ORG)

    app_names = App.get_apps(client.zephyr)

    db_releases = client.zephyr.app_releases
    db_commits = client.zephyr.release_commits
    repos = list(org.iter_repos())

    for r in repos:
        if r.name in app_names:
            print "Found", r.name
            for t in r.iter_tags():
                r_tag = db_releases.find_one({"_id": t.commit['sha']})
                if r_tag is not None:
                    continue
                log.info("Syncing release %s", t.name)

                d = t._json_data
                d['_id'] = d['commit']['sha']
                d['app'] = r.name
                db_releases.insert(d)

                log.info("Syncing commits %s", t.name)
                commits = r.iter_commits(d['_id'], number=10)
                for c in commits:
                    cd = c._json_data
                    cd['_id'] = cd['sha']
                    try:
                        db_commits.insert(cd, upsert=True)
                    except pymongo.errors.DuplicateKeyError:
                        continue


if __name__ == '__main__':
    main()
