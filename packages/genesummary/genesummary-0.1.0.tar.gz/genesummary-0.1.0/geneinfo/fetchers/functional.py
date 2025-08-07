"""
Functional annotation fetchers for Gene Ontology and Reactome APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Fetchers for functional annotation and pathway data
Version: 0.1
"""

import logging
from typing import Dict, List, Optional
from urllib.parse import quote

from ..mock_data import MOCK_GENE_DATA
from .base import BaseFetcher

logger = logging.getLogger(__name__)


class GOFetcher(BaseFetcher):
    """Fetcher for Gene Ontology information."""

    def __init__(self, use_mock: bool = None):
        super().__init__("http://api.geneontology.org", use_mock=use_mock)

        # Auto-detect if we should use mock data
        if use_mock is None:
            self.use_mock = self._should_use_mock()

    def _should_use_mock(self) -> bool:
        """Check if external API is accessible."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/bioentity/gene/TP53/function", timeout=5
            )
            return response.status_code != 200
        except Exception:
            return True

    def get_go_terms(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get Gene Ontology terms for a gene."""
        if self.use_mock:
            return self._get_mock_go_terms(gene_symbol)

        url = (
            f"{self.base_url}/api/bioentity/gene/{quote(gene_symbol)}/function"
        )
        result = self._make_request(url)

        if result and "associations" in result:
            go_terms = []
            for assoc in result["associations"]:
                go_info = {
                    "go_id": assoc.get("object", {}).get("id"),
                    "go_name": assoc.get("object", {}).get("label"),
                    "evidence_code": assoc.get("evidence_type"),
                    "aspect": assoc.get("object", {}).get("category"),
                    "qualifier": assoc.get("qualifiers", []),
                }
                go_terms.append(go_info)
            return go_terms

        return None

    def _get_mock_go_terms(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get mock GO terms."""
        gene_key = gene_symbol.upper()
        for mock_gene, data in MOCK_GENE_DATA.items():
            if (
                mock_gene == gene_key
                or data["basic_info"].get("external_name", "").upper()
                == gene_key
                or data["basic_info"].get("display_name", "").upper()
                == gene_key
            ):
                return data["gene_ontology"]
        return None


class ReactomeFetcher(BaseFetcher):
    """Fetcher for Reactome pathway information."""

    def __init__(self, use_mock: bool = None):
        super().__init__(
            "https://reactome.org/ContentService", use_mock=use_mock
        )

        # Auto-detect if we should use mock data
        if use_mock is None:
            self.use_mock = self._should_use_mock()

    def _should_use_mock(self) -> bool:
        """Check if external API is accessible."""
        try:
            response = self.session.get(
                f"{self.base_url}/data/pathways/low/entity/TP53/allForms?species=Homo sapiens",
                timeout=5,
            )
            return response.status_code != 200
        except Exception:
            return True

    def get_pathways(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get pathway information from Reactome."""
        if self.use_mock:
            return self._get_mock_pathways(gene_symbol)

        url = f"{self.base_url}/data/pathways/low/entity/{quote(gene_symbol)}/allForms"
        params = {"species": "Homo sapiens"}
        result = self._make_request(url, params)

        if result and isinstance(result, list):
            pathways = []
            for pathway in result:
                pathway_info = {
                    "pathway_id": pathway.get("stId"),
                    "name": pathway.get("displayName"),
                    "species": pathway.get("species", [{}])[0].get(
                        "displayName"
                    )
                    if pathway.get("species")
                    else None,
                    "url": f"https://reactome.org/content/detail/{pathway.get('stId')}"
                    if pathway.get("stId")
                    else None,
                }
                pathways.append(pathway_info)
            return pathways

        return None

    def _get_mock_pathways(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get mock pathway information."""
        gene_key = gene_symbol.upper()
        for mock_gene, data in MOCK_GENE_DATA.items():
            if (
                mock_gene == gene_key
                or data["basic_info"].get("external_name", "").upper()
                == gene_key
                or data["basic_info"].get("display_name", "").upper()
                == gene_key
            ):
                return data["pathways"]
        return None
