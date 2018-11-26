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

    @classmethod
    def load(cls, path):
        csv_in = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            path
        )
        with open(csv_in) as csvfile:
            rows = DictReader(csvfile)
            for row in rows:
                row['date'] = datetime.strptime(row['date'], '%m/%d/%Y')
                row['amount'] = int(row['amount'])
                transaction = cls(**row)
                transaction.save()


class FecCommittees(BaseModel):
    fecid = CharField(null=True)
    name = CharField(null=True)
    treasurer = CharField(null=True)
    address_one = CharField(null=True)
    address_two = CharField(null=True)
    city = CharField(null=True)
    state = CharField(null=True)
    zip = CharField(null=True)
    designation = CharField(null=True)
    committee_type = CharField(null=True)
    party = CharField(null=True)
    filing_frequency = CharField(null=True)
    interest_group = CharField(null=True)
    organization = CharField(null=True)
    fec_candidate_id = CharField(null=True)
    cycle = CharField(null=True)
    is_leadership = CharField(null=True)
    is_super_pac = CharField(null=True)

    @classmethod
    def load(cls, path):
        csv_in = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            path
        )
        with open(csv_in) as csvfile:
            rows = DictReader(csvfile)
            for row in rows:
                transaction = cls(**row)
                transaction.save()



class FecCandidates(BaseModel):
    fecid = CharField(null=True)
    party = CharField(null=True)
    status = CharField(null=True)
    address_one = CharField(null=True)
    address_two = CharField(null=True)
    city = CharField(null=True)
    state = CharField(null=True)
    zip = CharField(null=True)
    fec_committee_id = CharField(null=True)
    cycle = CharField(null=True)
    district = CharField(null=True)
    office_state = CharField(null=True)
    cand_status = CharField(null=True)
    branch = CharField(null=True)

    @classmethod
    def load(cls, path):
        csv_in = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            path
        )
        with open(csv_in) as csvfile:
            rows = DictReader(csvfile)
            for row in rows:
                transaction = cls(**row)
                transaction.save()
