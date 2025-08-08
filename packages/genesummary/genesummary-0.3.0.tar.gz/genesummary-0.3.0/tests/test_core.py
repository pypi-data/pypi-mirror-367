# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Tests for core GeneInfo class
# Version: 0.1

"""
Tests for core GeneInfo functionality.
"""

import json
from unittest.mock import Mock, patch

import pytest

from geneinfo.core import GeneInfo
from geneinfo.mock_data import MOCK_GENE_DATA


class TestGeneInfo:
    """Test cases for GeneInfo class."""

    def test_init(self):
        """Test GeneInfo initialization."""
        gene_info = GeneInfo(species="human")
        assert gene_info.species == "human"
        assert hasattr(gene_info, "ensembl_fetcher")
        assert hasattr(gene_info, "uniprot_fetcher")
        assert hasattr(gene_info, "go_fetcher")
        assert hasattr(gene_info, "reactome_fetcher")

    def test_init_different_species(self):
        """Test GeneInfo initialization with different species."""
        gene_info = GeneInfo(species="mouse")
        assert gene_info.species == "mouse"

    @patch("geneinfo.core.EnsemblFetcher")
    @patch("geneinfo.core.UniProtFetcher")
    @patch("geneinfo.core.GOFetcher")
    @patch("geneinfo.core.ReactomeFetcher")
    def test_get_gene_info_structure(
        self, mock_reactome, mock_go, mock_uniprot, mock_ensembl
    ):
        """Test that get_gene_info returns proper structure."""
        # Mock the fetchers
        mock_ensembl_instance = Mock()
        mock_ensembl_instance.get_gene_info.return_value = MOCK_GENE_DATA[
            "TP53"
        ]["basic_info"]
        mock_ensembl_instance.get_transcripts.return_value = MOCK_GENE_DATA[
            "TP53"
        ]["transcripts"]
        mock_ensembl_instance.get_homologs.return_value = {
            "orthologs": MOCK_GENE_DATA["TP53"].get("orthologs", []),
            "paralogs": MOCK_GENE_DATA["TP53"].get("paralogs", []),
        }
        mock_ensembl.return_value = mock_ensembl_instance

        mock_uniprot_instance = Mock()
        mock_uniprot_instance.get_protein_domains.return_value = MOCK_GENE_DATA[
            "TP53"
        ].get("protein_domains", [])
        mock_uniprot_instance.get_protein_interactions.return_value = (
            MOCK_GENE_DATA["TP53"].get("protein_interactions", [])
        )
        mock_uniprot.return_value = mock_uniprot_instance

        mock_go_instance = Mock()
        mock_go_instance.get_go_terms.return_value = MOCK_GENE_DATA["TP53"].get(
            "gene_ontology", []
        )
        mock_go.return_value = mock_go_instance

        mock_reactome_instance = Mock()
        mock_reactome_instance.get_pathways.return_value = MOCK_GENE_DATA[
            "TP53"
        ].get("pathways", [])
        mock_reactome.return_value = mock_reactome_instance

        gene_info = GeneInfo()
        result = gene_info.get_gene_info("TP53")

        # Check structure
        expected_keys = [
            "query",
            "basic_info",
            "transcripts",
            "protein_domains",
            "gene_ontology",
            "pathways",
            "protein_interactions",
            "paralogs",
            "orthologs",
        ]
        for key in expected_keys:
            assert key in result

        assert result["query"] == "TP53"

    def test_get_gene_info_empty_input(self):
        """Test get_gene_info with empty input."""
        gene_info = GeneInfo()

        with pytest.raises((ValueError, TypeError)):
            gene_info.get_gene_info("")

    def test_get_gene_info_none_input(self):
        """Test get_gene_info with None input."""
        gene_info = GeneInfo()

        with pytest.raises((ValueError, TypeError)):
            gene_info.get_gene_info(None)
