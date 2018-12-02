import csv, sys
from sys import stdout
from pandas import *
import MySQLdb
import numpy as np
from models import *

def initial_setup():
    # Check if these tables have been created first

	print('Creating table fec_candidates')
	FecCandidates.create_table()
	print('Loading data for fec_candidates')
	FecCandidates.load('csv/fec_candidates.csv')

	print('Creating table fec_committees')
	FecCommittees.create_table()
	print('Loading data for fec_committees')
	FecCommittees.load('csv/fec_committees.csv')

	print('Creating table fec_committee_contributions')
	FecCommitteeContributions.create_table()
	print('Loading data for fec_committee_contributions')
	FecCommitteeContributions.load('csv/fec_committee_contributions.csv')

	print('Creating table fec_contributions')
	FecContributions.create_table()
	print('Loading data for fec_contributions')
	FecContributions.load()

	print("Initial setup done")

def compute_exclusivity_scores():
    TotalDonatedByContributor.insert_from(
        FecContributions\
            .select(
                FecContributions.fec_committee_id,
                FecContributions.contributor_name,
                fn.Sum(FecContributions.amount).alias('total_by_PAC')
            )\
            .group_by(
                FecContributions.fec_committee_id,
                FecContributions.contributor_name
            ),
        fields=[
            TotalDonatedByContributor.fec_committee_id,
            TotalDonatedByContributor.contributor_name,
            TotalDonatedByContributor.total_by_PAC
        ]
    )

    TotalDonatedByContributor.insert_from(
        FecContributions\
            .select(
                FecContributions.fec_committee_id,
                FecContributions.contributor_name,
                fn.Sum(FecContributions.amount).alias('total_by_PAC')
            )\
            .group_by(
                FecContributions.fec_committee_id,
                FecContributions.contributor_name
            ),
        fields=[
            TotalDonatedByContributor.fec_committee_id,
            TotalDonatedByContributor.contributor_name,
            TotalDonatedByContributor.total_by_PAC
        ]
    )
