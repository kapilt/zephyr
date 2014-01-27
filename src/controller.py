import operator


class App(object):

    def __init__(self, db, name, stage=None):
        self.db = db
        self.name = name
        self.stage = stage

    def get_instances(self):
        instances = list(self.db.instances.find(
            {'State.Code': 16,
             'Tags': {'$elemMatch': {'Key': 'site', 'Value': self.name}}},
            as_class=Instance))

        if not self.stage:
            return instances

        def filter_stage(i):
            for t in i['Tags']:
                if t['Key'] == 'op_env':
                    if t['Value'] == self.stage:
                        return True
        return sorted(
            filter(filter_stage, instances),
            key=operator.attrgetter('name'))

    def get_dbs(self):
        dbs = list(self.db.databases.find())
        results = []
        for d in dbs:
            if self.name in d['DBInstanceIdentifier'].replace('-', '.'):
                if self.stage:
                    print "stage", self.stage, d['DBInstanceIdentifier']
                    if self.stage in d['DBInstanceIdentifier']:
                        results.append(d)
                else:
                    results.append(d)
        return results

    def get_loadbalancers(self):
        pass

    def get_change_tickets(self, labels=()):
        tickets = []
        if labels:
            if not isinstance(labels, (tuple, list)):
                labels = [labels]
            tickets.extend(list(self.db.cm_issues.find(
                {'labels': {'$in': labels}})))
        tickets.extend(list(self.db.cm_issues.find(
            {'sites': {'$in': [self.name]}})))
        return tickets

    @staticmethod
    def get_apps(db):
        tags = db.instances.find(
            {'State.Code': 16}, fields={'Tags': True, '_id': False})
        apps = set()
        for t in tags:
            for kv in t['Tags']:
                if kv['Key'] == 'site':
                    sites = kv['Value']
                    if ',' in sites:
                        sites = [s.strip() for s in sites.split(",")]
                    elif ':' in sites:
                        sites = [s.strip() for s in sites.split(":")]
                    else:
                        sites = [sites]

                    for s in sites:
                        apps.add(s)
        return apps


class Instance(dict):

    __slots__ = ()

    @property
    def name(self):
        for t in self['Tags']:
            if t['Key'] == "Name":
                return t['Value']
        return "Unknown"
