"""

Cost estimation by resource allocation.

DOES NOT TAKE INTO ACCOUNT FULL COSTS (TRAFFIC/IO/USAGE).
"""

import pymongo
from decimal import Decimal


TYPE_RATE_MAPPING = {
    "t1.micro": Decimal("0.02"),
    "m1.small": Decimal("0.060"),
    "m1.medium": Decimal("0.120"),
    "m1.large": Decimal("0.240"),
    "m1.xlarge": Decimal("0.480"),
    "m3.xlarge": Decimal("0.450"),
    "m3.2xlarge": Decimal("0.900"),
    "c3.large": Decimal("0.150"),
    "c3.xlarge": Decimal("0.300"),
    "c3.2xlarge": Decimal("0.600"),
    "c1.medium": Decimal("0.17"),
    "c1.xlarge": Decimal("0.68"),
    "m2.xlarge": Decimal("0.50"),
    "m2.2xlarge": Decimal("1.00"),
    "m2.4xlarge": Decimal("2.00"),
    "cc1.4xlarge": Decimal("1.60"),
    "cg1.4xlarge": Decimal("2.10"),
    # Databases
    "db.m1.xlarge": Decimal("2.00")}


MONTH_HOURS = 24 * 30


def get_instance_monthly_cost(instances):
    cost = 0
    for i in instances:
        itype = i['InstanceType']
        if itype not in TYPE_RATE_MAPPING:
            raise ValueError("Unknown instance type %s" % itype)
        cost += TYPE_RATE_MAPPING[itype] * MONTH_HOURS
    return cost


def get_db_monthly_cost(dbs):
    cost = 0
    for i in dbs:
        itype = i['DBInstanceClass']
        if itype not in TYPE_RATE_MAPPING:
            raise ValueError("Unknown db type %s" % itype)
        cost += TYPE_RATE_MAPPING[itype] * MONTH_HOURS
    return cost


def main():
    client = pymongo.MongoClient()
    from controller import App
    app = App(client.zephyr, "cms.nasa.gov")
    instances = list(app.get_instances())
    print get_instance_monthly_cost(instances)

    dbs = list(app.get_dbs())
    print get_db_monthly_cost(dbs)


if __name__ == '__main__':
    try:
        main()
    except:
       import pdb, traceback, sys
       traceback.print_exc()
       pdb.post_mortem(sys.exc_info()[-1])
