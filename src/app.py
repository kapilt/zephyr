import json
import pprint
from pymongo import MongoClient
from flask import Flask, render_template


app = Flask('zephyr')
app.debug = True

client = MongoClient()
db = client.zephyr


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
