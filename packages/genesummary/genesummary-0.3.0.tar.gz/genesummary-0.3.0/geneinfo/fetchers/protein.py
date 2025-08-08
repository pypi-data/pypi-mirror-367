"""
Protein data fetchers for UniProt and STRING-db APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Fetchers for protein domain and interaction data
Version: 0.1
"""

import logging
import time
from typing import Dict, List, Optional

from .base import BaseFetcher

logger = logging.getLogger(__name__)


class UniProtFetcher(BaseFetcher):
    """Fetcher for UniProt API."""

    def __init__(self):
        super().__init__("https://rest.uniprot.org")

    def get_protein_domains(self, protein_id: str) -> Optional[List[Dict]]:
        """Get protein domain information from UniProt."""
        # Convert Ensembl protein ID to UniProt if needed
        uniprot_id = self._get_uniprot_id(protein_id)
        if not uniprot_id:
            return None

        url = f"{self.base_url}/uniprotkb/{uniprot_id}.json"
        result = self._make_request(url)

        if result and "features" in result:
            domains = []
            for feature in result["features"]:
                if feature.get("type") in ["DOMAIN", "REGION", "MOTIF"]:
                    domain_info = {
                        "type": feature.get("type"),
                        "description": feature.get("description"),
                        "start": feature.get("location", {})
                        .get("start", {})
                        .get("value"),
                        "end": feature.get("location", {})
                        .get("end", {})
                        .get("value"),
                        "evidence": feature.get("evidences", []),
                    }
                    domains.append(domain_info)
            return domains

        return None

    def get_protein_interactions(self, protein_id: str) -> Optional[List[Dict]]:
        """Get protein-protein interactions."""
        # This is a simplified implementation
        # In a real scenario, you'd use STRING-db or IntAct APIs
        return []

    def _get_uniprot_id(self, protein_id: str) -> Optional[str]:
        """Convert Ensembl protein ID to UniProt ID."""
        if not protein_id.startswith("ENSP"):
            return protein_id  # Assume it's already UniProt

        url = f"{self.base_url}/idmapping/run"
        data = {"from": "Ensembl_Protein", "to": "UniProtKB", "ids": protein_id}

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            job_id = response.json().get("jobId")

            if job_id:
                # Poll for results
                status_url = f"{self.base_url}/idmapping/status/{job_id}"
                for _ in range(10):  # Max 10 attempts
                    time.sleep(1)
                    status_response = self.session.get(status_url)
                    if status_response.status_code == 200:
                        results_url = (
                            f"{self.base_url}/idmapping/results/{job_id}"
                        )
                        results_response = self.session.get(results_url)
                        if results_response.status_code == 200:
                            results = results_response.json()
                            if (
                                "results" in results
                                and len(results["results"]) > 0
                            ):
                                return results["results"][0]["to"]
                        break

        except Exception as e:
            logger.error(f"Error converting protein ID {protein_id}: {str(e)}")

        return None


class StringDBFetcher(BaseFetcher):
    """Fetcher for STRING-db protein-protein interactions."""

    def __init__(self, species: str = "9606"):
        # Use HTTPS with SSL verification disabled due to certificate issues
        super().__init__("https://string-db.org/api")
        self.species = species  # NCBI taxon ID (9606 for human)

        # Disable SSL verification for STRING-db due to certificate issues
        self.session.verify = False

    def get_protein_interactions(
        self, gene_symbol: str
    ) -> Optional[List[Dict]]:
        """Get protein-protein interactions from STRING-db."""
        try:
            # First, map the gene symbol to STRING ID
            string_id = self._get_string_id(gene_symbol)
            if not string_id:
                logger.warning(f"Could not map {gene_symbol} to STRING ID")
                return None

            # Get interaction partners
            url = f"{self.base_url}/json/interaction_partners"
            params = {
                "identifiers": string_id,
                "species": self.species,
                "limit": 50,  # Limit to top 50 interactions
                "required_score": 400,  # Medium confidence threshold
                "caller_identity": "geneinfo_v0.1",
            }

            # Use POST as recommended by STRING API
            response = self.session.post(url, data=params, timeout=30)
            response.raise_for_status()

            # Wait 1 second as requested by STRING API
            time.sleep(1)

            result = response.json()

            if result and isinstance(result, list):
                interactions = []
                for interaction in result:
                    interaction_info = {
                        "partner_id": interaction.get("stringId_B"),
                        "partner_name": interaction.get("preferredName_B"),
                        "combined_score": interaction.get("score"),
                        "experimental_score": interaction.get("escore"),
                        "database_score": interaction.get("dscore"),
                        "textmining_score": interaction.get("tscore"),
                        "coexpression_score": interaction.get("ascore"),
                        "evidence_types": self._get_evidence_types(interaction),
                    }
                    interactions.append(interaction_info)

                return interactions if interactions else None

            return None

        except Exception as e:
            logger.error(
                f"Error fetching STRING-db interactions for {gene_symbol}: {str(e)}"
            )
            return None

    def _get_string_id(self, gene_symbol: str) -> Optional[str]:
        """Map gene symbol to STRING identifier."""
        try:
            url = f"{self.base_url}/json/get_string_ids"
            params = {
                "identifiers": gene_symbol,
                "species": self.species,
                "echo_query": 1,
                "caller_identity": "geneinfo_v0.1",
            }

            response = self.session.post(url, data=params, timeout=30)
            response.raise_for_status()

            # Wait 1 second as requested by STRING API
            time.sleep(1)

            result = response.json()

            if result and isinstance(result, list) and len(result) > 0:
                # Return the first (best) match
                return result[0].get("stringId")

            return None

        except Exception as e:
            logger.error(f"Error mapping {gene_symbol} to STRING ID: {str(e)}")
            return None

    def _get_evidence_types(self, interaction: Dict) -> List[str]:
        """Extract evidence types based on scores."""
        evidence_types = []
        scores = {
            "experimental": interaction.get("escore", 0),
            "database": interaction.get("dscore", 0),
            "textmining": interaction.get("tscore", 0),
            "coexpression": interaction.get("ascore", 0),
            "neighborhood": interaction.get("nscore", 0),
            "fusion": interaction.get("fscore", 0),
            "phylogenetic": interaction.get("pscore", 0),
        }

        for evidence_type, score in scores.items():
            if score and float(score) > 0.1:  # Only include if score > 0.1
                evidence_types.append(evidence_type)

        return evidence_types
