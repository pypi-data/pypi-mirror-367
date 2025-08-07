# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Tests for data fetchers
# Version: 0.1

"""
Tests for data fetchers.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from geneinfo.fetchers import (
    BaseFetcher,
    EnsemblFetcher,
    GOFetcher,
    ReactomeFetcher,
    UniProtFetcher,
)


class TestBaseFetcher:
    """Test cases for BaseFetcher class."""

    def test_init(self):
        """Test BaseFetcher initialization."""
        fetcher = BaseFetcher("http://example.com", rate_limit=0.1)
        assert fetcher.base_url == "http://example.com"
        assert fetcher.rate_limit == 0.1
        assert not fetcher.use_mock
        assert hasattr(fetcher, "session")

    def test_init_with_mock(self):
        """Test BaseFetcher initialization with mock enabled."""
        fetcher = BaseFetcher("http://example.com", use_mock=True)
        assert fetcher.use_mock

    @patch("geneinfo.fetchers.base.requests.Session.get")
    @patch("time.sleep")
    def test_make_request_success(self, mock_sleep, mock_get):
        """Test successful API request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fetcher = BaseFetcher("http://example.com")
        result = fetcher._make_request("http://example.com/test")

        assert result == {"test": "data"}
        mock_sleep.assert_called_once_with(0.1)
        mock_get.assert_called_once()

    @patch("geneinfo.fetchers.base.requests.Session.get")
    @patch("time.sleep")
    def test_make_request_http_error(self, mock_sleep, mock_get):
        """Test API request with HTTP error."""
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")

        fetcher = BaseFetcher("http://example.com")
        result = fetcher._make_request("http://example.com/test")

        assert result is None

    @patch("geneinfo.fetchers.base.requests.Session.get")
    @patch("time.sleep")
    def test_make_request_with_mock(self, mock_sleep, mock_get):
        """Test API request with mock enabled."""
        fetcher = BaseFetcher("http://example.com", use_mock=True)
        result = fetcher._make_request("http://example.com/test")

        assert result is None
        mock_get.assert_not_called()
        mock_sleep.assert_not_called()


class TestEnsemblFetcher:
    """Test cases for EnsemblFetcher class."""

    def test_init(self):
        """Test EnsemblFetcher initialization."""
        fetcher = EnsemblFetcher("human")
        assert (
            fetcher.species == "homo_sapiens"
        )  # "human" maps to "homo_sapiens"
        assert "ensembl" in fetcher.base_url

    def test_init_mouse(self):
        """Test EnsemblFetcher initialization with mouse."""
        fetcher = EnsemblFetcher("mouse")
        assert fetcher.species == "mouse"


class TestUniProtFetcher:
    """Test cases for UniProtFetcher class."""

    def test_init(self):
        """Test UniProtFetcher initialization."""
        fetcher = UniProtFetcher()
        assert "uniprot" in fetcher.base_url


class TestGOFetcher:
    """Test cases for GOFetcher class."""

    def test_init(self):
        """Test GOFetcher initialization."""
        fetcher = GOFetcher()
        assert (
            "ebi.ac.uk" in fetcher.base_url
            or "ontology" in fetcher.base_url.lower()
        )


class TestReactomeFetcher:
    """Test cases for ReactomeFetcher class."""

    def test_init(self):
        """Test ReactomeFetcher initialization."""
        fetcher = ReactomeFetcher()
        assert "reactome" in fetcher.base_url
