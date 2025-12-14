"""Tests for FEC data fetchers."""

import pytest

from bedfellows.fetchers.base import BaseFetcher
from bedfellows.fetchers.candidates import CandidateFetcher


class TestBaseFetcher:
    """Tests for BaseFetcher class."""

    def test_build_url_with_year_path(self):
        """Test that build_url constructs year-based paths correctly."""
        fetcher = BaseFetcher()
        
        # Test with year and filename
        url = fetcher.build_url("2026", "weball26.zip")
        assert url == "https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/2026/weball26.zip"
        
    def test_build_url_no_trailing_slash(self):
        """Test build_url with base URL without trailing slash."""
        fetcher = BaseFetcher(base_url="https://example.com/base")
        
        url = fetcher.build_url("2024", "file.zip")
        assert url == "https://example.com/base/2024/file.zip"
        
    def test_build_url_with_leading_slash(self):
        """Test build_url with parts that have leading slashes."""
        fetcher = BaseFetcher(base_url="https://example.com/base/")
        
        url = fetcher.build_url("/2024", "/file.zip")
        assert url == "https://example.com/base/2024/file.zip"
        
    def test_build_url_single_part(self):
        """Test build_url with single part."""
        fetcher = BaseFetcher()
        
        url = fetcher.build_url("cn.txt")
        assert url == "https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/cn.txt"


class TestCandidateFetcher:
    """Tests for CandidateFetcher class."""
    
    def test_candidate_master_url(self):
        """Test that candidate master file URL is constructed correctly."""
        fetcher = CandidateFetcher()
        
        # Test 2026 cycle
        url = fetcher.build_url("2026", "weball26.zip")
        expected = "https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/2026/weball26.zip"
        assert url == expected
        
    def test_2024_cycle_url(self):
        """Test 2024 cycle URL."""
        fetcher = CandidateFetcher()
        
        url = fetcher.build_url("2024", "weball24.zip")
        expected = "https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/2024/weball24.zip"
        assert url == expected
        
    def test_all_cycles_url(self):
        """Test that all cycles file URL is constructed correctly."""
        fetcher = CandidateFetcher()
        
        url = fetcher.build_url("cn.txt")
        expected = "https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/cn.txt"
        assert url == expected
