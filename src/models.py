from mongoengine import DynamicDocument, connect, connection

import botocore.session
import datetime

CREATED = 1
MODIFIED = 2
NOCHANGE = 3


def _call(s, svc, op, region, *args, **kw):
    """ Call a method against the boto api and return the result.
             - s: boto session,
             - svc: service operation name
             - region: region name to operate agains.

    """
    svc = s.get_service(svc)
    op = svc.get_operation(op)
    ep = svc.get_endpoint(region)
    response, data = op.call(ep, *args, **kw)
    return data


def _sync(cls, key, src):
    tgt, created = cls.objects.get_or_create(awsid=src[key])
    modified = set()

    for k, v in src.items():
        t_v = getattr(tgt, k, None)
        if t_v != v:
            setattr(tgt, k, v)
            modified.add(k)

    if created:
        tgt.ctime = datetime.datetime.utcnow()
        tgt.awsid = src[key]

    elif modified:
        print "Modified", src[key], modified
        data = tgt.to_mongo()
        data['res_class'] = cls.__name__.lower()
        del data['_id']
        db = connection.get_db()
        db.versions.insert(data, w=1)

    if created or modified:
        tgt.ltime = datetime.datetime.utcnow()
        tgt.save()
    if created:
        return CREATED
    if modified:
        return MODIFIED
    return NOCHANGE


class Image(DynamicDocument):
    meta = {'collection': "images"}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'ec2', 'DescribeImages', region, owners=['self'])
        for r_img in data.get("Images", ()):
            _sync(cls, "ImageId", r_img)


class Snapshot(DynamicDocument):
    meta = {'collection': "snapshots"}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'ec2', 'DescribeSnapshots', region, owner_ids=['self'])
        for r_snap in data.get('Snapshots', ()):
            _sync(cls, "SnapshotId", r_snap)


class Volume(DynamicDocument):
    meta = {'collection': "volumes"}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'ec2', 'DescribeVolumes', region)
        for r_vol in data.get('Volumes', ()):
            _sync(cls, "VolumeId", r_vol)


class Instance(DynamicDocument):
    meta = {"collection": "instances"}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'ec2', 'DescribeInstances', region)
        for r in data.get('Reservations', ()):
            for i in r.get('Instances', ()):
                _sync(cls, "InstanceId", i)


class Database(DynamicDocument):
    meta = {'collection': "databases"}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'rds', 'DescribeDBInstances', region)
        for r_db in data.get('DBInstances', ()):
            _sync(cls, "DBInstanceIdentifier", r_db)


class LoadBalancer(DynamicDocument):
    meta = {'collection': "load_balancers"}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'elb', 'DescribeLoadBalancers', region)
        for r_elb in data.get('LoadBalancerDescriptions', ()):
            _sync(cls, "LoadBalancerName", r_elb)


class Bucket(DynamicDocument):
    meta = {'collection': 'buckets'}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 's3', 'ListBuckets', region)
        for r_b in data.get("Buckets", ()):
            _sync(cls, "Name", r_b)


class IamUser(DynamicDocument):
    meta = {'collection': 'iam_users'}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'iam', 'ListUsers', region)
        for r_u in data.get('Users', ()):
            _sync(cls, "UserName", r_u)


class DnsEntry(DynamicDocument):
    meta = {'collection': 'dns_entries'}

    @classmethod
    def sync(cls, session, region):
        data = _call(session, 'route53', 'ListHostedZones', region)
        for r_h in data.get('HostedZones', ()):
            _, hid = r_h['Id'].rsplit("/", 1)
            r_data = _call(
                session, 'route53', 'ListResourceRecordSets', region,
                hosted_zone_id=hid)
            for r_e in r_data.get('ResourceRecordSets', ()):
                _sync(cls, "Name", r_e)


def sync(session, region):
    Image.sync(session, region)
    print "Images", len(Image.objects)

    Snapshot.sync(session, region)
    print "Snapshots", len(Snapshot.objects)

    Volume.sync(session, region)
    print "Volumes", len(Volume.objects)

    Instance.sync(session, region)
    print "Instances", len(Instance.objects)

    Bucket.sync(session, region)
    print "Buckets", len(Bucket.objects)

    LoadBalancer.sync(session, region)
    print "Load Balancers", len(LoadBalancer.objects)

    Database.sync(session, region)
    print "Database", len(Database.objects)

    DnsEntry.sync(session, region)
    print "Dns Entries", len(DnsEntry.objects)

    IamUser.sync(session, region)
    print "IAM Users", len(IamUser.objects)


def main():
    connect('zephyr')
    session = botocore.session.get_session()
    sync(session, 'us-east-1')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        import pdb, sys, traceback
        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[-1])
        raise
        
