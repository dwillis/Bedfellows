from peewee import *
from csv import DictReader
from datetime import datetime
import os
import pdb

database = MySQLDatabase(
    'fec',
    user='root',
    password='root',
    host='localhost'
)

class BaseModel(Model):
    class Meta:
        database = database

class FecTransaction(BaseModel):
    fec_committee_id = CharField(null=True)
    amendment = CharField(null=True)
    report_type = CharField(null=True)
    pgi = CharField(null=True)
    microfilm = CharField(null=True)
    transaction_type = CharField(null=True)
    entity_type = CharField(null=True)
    contributor_name = CharField(null=True)
    city = CharField(null=True)
    state = CharField(null=True)
    zipcode =  CharField(null=True)
    employer = CharField(null=True)
    occupation = CharField(null=True)
    date = DateTimeField(null=True)
    amount = IntegerField(null=True)
    other_id = CharField(null=True)
    recipient_name = CharField(null=True)
    recipient_state = CharField(null=True)
    recipient_party = CharField(null=True)
    cycle = CharField(null=True)
    transaction_id = CharField(null=True)
    filing_id = CharField(null=True)
    memo_code = CharField(null=True)
    memo_text = CharField(null=True)
    fec_record_number = CharField(null=True)

