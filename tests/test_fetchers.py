"""Tests for FEC data fetchers."""

import pytest

from bedfellows.fetchers.base import BaseFetcher
from bedfellows.fetchers.candidates import CandidateFetcher


class TestBaseFetcher:
    """Tests for BaseFetcher class."""

    def test_build_url_no_duplication(self):
        """Test that build_url doesn't duplicate path segments."""
        fetcher = BaseFetcher(base_url="https://www.fec.gov/files/bulk-downloads/")
        
        # Test with trailing slash on base_url
        url = fetcher.build_url("bulk-downloads", "weball26.zip")
        assert url == "https://www.fec.gov/files/bulk-downloads/bulk-downloads/weball26.zip"
        assert "bulk-downloads/bulk-downloads/bulk-downloads" not in url
        
    def test_build_url_no_trailing_slash(self):
        """Test build_url with base URL without trailing slash."""
        fetcher = BaseFetcher(base_url="https://www.fec.gov/files/bulk-downloads")
        
        url = fetcher.build_url("bulk-downloads", "weball26.zip")
        assert url == "https://www.fec.gov/files/bulk-downloads/bulk-downloads/weball26.zip"
        
    def test_build_url_with_leading_slash(self):
        """Test build_url with parts that have leading slashes."""
        fetcher = BaseFetcher(base_url="https://www.fec.gov/files/bulk-downloads/")
        
        url = fetcher.build_url("/bulk-downloads", "/weball26.zip")
        assert url == "https://www.fec.gov/files/bulk-downloads/bulk-downloads/weball26.zip"
        
    def test_build_url_single_part(self):
        """Test build_url with single part."""
        fetcher = BaseFetcher(base_url="https://www.fec.gov/files/bulk-downloads")
        
        url = fetcher.build_url("cn.txt")
        assert url == "https://www.fec.gov/files/bulk-downloads/cn.txt"


class TestCandidateFetcher:
    """Tests for CandidateFetcher class."""
    
    def test_candidate_master_url(self):
        """Test that candidate master file URL is constructed correctly."""
        fetcher = CandidateFetcher()
        
        # Test 2026 cycle
        url = fetcher.build_url("bulk-downloads", "weball26.zip")
        expected = "https://www.fec.gov/files/bulk-downloads/bulk-downloads/weball26.zip"
        assert url == expected
        
        # Ensure no duplication
        assert url.count("bulk-downloads") == 2  # Should appear exactly twice
        
    def test_all_cycles_url(self):
        """Test that all cycles file URL is constructed correctly."""
        fetcher = CandidateFetcher()
        
        url = fetcher.build_url("bulk-downloads", "cn.txt")
        expected = "https://www.fec.gov/files/bulk-downloads/bulk-downloads/cn.txt"
        assert url == expected
