

import pymongo
from decimal import Decimal

client = pymongo.MongoClient()


TYPE_RATE_MAPPING = {
    "t1.micro": Decimal("0.02"),
    "m1.small": Decimal("0.060"),
    "m1.medium": Decimal("0.120"),
    "m1.large": Decimal("0.240"),
    "m1.xlarge": Decimal("0.480"),
    "m3.xlarge": None,
    "m3.2xlarge": None,
    "c1.medium": Decimal("0.17"),
    "c1.xlarge": Decimal("0.68"),
    "m2.xlarge": Decimal("0.50"),
    "m2.2xlarge": Decimal("1.00"),
    "m2.4xlarge": Decimal("2.00"),
    "cc1.4xlarge": Decimal("1.60"),
    "cg1.4xlarge": Decimal("2.10")}




def main():
    
