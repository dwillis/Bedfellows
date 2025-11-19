"""
FEC data fetcher modules for downloading bulk data from fec.gov.
"""

from bedfellows.fetchers.base import BaseFetcher
from bedfellows.fetchers.candidates import CandidateFetcher
from bedfellows.fetchers.committees import CommitteeFetcher
from bedfellows.fetchers.contributions import ContributionFetcher

__all__ = [
    "BaseFetcher",
    "CandidateFetcher",
    "CommitteeFetcher",
    "ContributionFetcher",
]
