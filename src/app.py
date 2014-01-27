import pprint

from pymongo import MongoClient
from flask import Flask, render_template

from controller import App

app = Flask('zephyr')
app.debug = True

client = MongoClient()
db = client.zephyr


@app.route("/apps/<app_name>")
def app_overview(app_name):
    a = App(db, app_name)
    return render_template('app-overview.j2', app=a)


@app.route("/apps")
def apps():
    apps = App.get_apps(db)
    return render_template('apps-index.j2', apps=sorted(apps))


@app.route("/")
def index():
    instances = list(db.instances.find())
    return render_template(
        'index.j2', instances=instances)


@app.route("/instance/<instance_id>")
def instance(instance_id):
    instance = db.instances.find_one({"awsid": instance_id})
    pprint.pprint(instance)
    return "hello world"


def main():
    app.run()

if __name__ == '__main__':
    main()
