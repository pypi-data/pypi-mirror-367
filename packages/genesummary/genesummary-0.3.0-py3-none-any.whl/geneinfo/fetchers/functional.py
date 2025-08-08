"""
Functional data fetchers for Gene Ontology and Reactome APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Fetchers for functional annotation and pathway data
Version: 0.1
"""

import logging
from typing import Dict, List, Optional

from .base import BaseFetcher

logger = logging.getLogger(__name__)


class GOFetcher(BaseFetcher):
    """Fetcher for Gene Ontology annotations."""

    def __init__(self):
        super().__init__("http://api.geneontology.org")

    def get_go_terms(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get GO terms for a gene."""
        try:
            # Use the GO API to search for gene associations
            url = f"{self.base_url}/api/bioentity/gene/{gene_symbol}/function"
            response = self._make_request(url)

            if response and "associations" in response:
                go_terms = []
                for assoc in response["associations"][:50]:  # Limit to 50
                    go_term = {
                        "go_id": assoc.get("object", {}).get("id"),
                        "term": assoc.get("object", {}).get("label"),
                        "category": assoc.get("object", {}).get("category"),
                        "evidence": assoc.get("evidence"),
                        "qualifier": assoc.get("qualifiers"),
                    }
                    go_terms.append(go_term)
                return go_terms
        except Exception as e:
            logger.error(f"Error fetching GO terms for {gene_symbol}: {str(e)}")
        return None


class ReactomeFetcher(BaseFetcher):
    """Fetcher for Reactome pathway data."""

    def __init__(self):
        super().__init__("https://reactome.org/ContentService")

    def get_pathways(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get Reactome pathways for a gene."""
        try:
            # First, try to find the identifier
            url = f"{self.base_url}/data/query/{gene_symbol}"
            response = self._make_request(url)

            if response and len(response) > 0:
                pathways = []
                for item in response[:10]:  # Limit to 10 pathways
                    if item.get("className") == "Pathway":
                        pathway_info = {
                            "pathway_id": item.get("stId"),
                            "name": item.get("displayName"),
                            "species": item.get("speciesName"),
                            "url": f"https://reactome.org/content/detail/{item.get('stId')}",
                        }
                        pathways.append(pathway_info)
                return pathways
        except Exception as e:
            logger.error(f"Error fetching pathways for {gene_symbol}: {str(e)}")
        return None
