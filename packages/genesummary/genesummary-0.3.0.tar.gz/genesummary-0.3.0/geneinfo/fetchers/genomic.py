"""
Genomic data fetchers for Ensembl and MyGene.info APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Fetchers for genomic annotation and gene information
Version: 0.1
"""

import logging
import ssl
from typing import Dict, List, Optional

from .base import BaseFetcher

logger = logging.getLogger(__name__)


class EnsemblFetcher(BaseFetcher):
    """Fetcher for Ensembl REST API."""

    def __init__(self, species: str = "human"):
        super().__init__("https://rest.ensembl.org")
        self.species = "homo_sapiens" if species.lower() == "human" else species
        self.session.headers.update({"Content-Type": "application/json"})

    def get_gene_info(self, gene_id: str) -> Optional[Dict]:
        """Get basic gene information from Ensembl."""
        # Try different endpoints based on input type
        if gene_id.startswith("ENSG"):
            url = f"{self.base_url}/lookup/id/{gene_id}"
        else:
            url = f"{self.base_url}/lookup/symbol/{self.species}/{gene_id}"

        params = {"expand": "1"}
        response = self._make_request(url, params)

        if response:
            return {
                "id": response.get("id"),
                "display_name": response.get("display_name"),
                "external_name": response.get("external_name"),
                "description": response.get("description"),
                "seq_region_name": response.get("seq_region_name"),
                "start": response.get("start"),
                "end": response.get("end"),
                "strand": response.get("strand"),
                "biotype": response.get("biotype"),
            }
        return None

    def get_transcripts(self, ensembl_id: str) -> Optional[List[Dict]]:
        """Get transcript information for a gene."""
        url = f"{self.base_url}/lookup/id/{ensembl_id}"
        params = {"expand": "1"}
        response = self._make_request(url, params)

        if response and "Transcript" in response:
            transcripts = []
            for transcript in response["Transcript"]:
                transcript_info = {
                    "id": transcript.get("id"),
                    "display_name": transcript.get("display_name"),
                    "biotype": transcript.get("biotype"),
                    "start": transcript.get("start"),
                    "end": transcript.get("end"),
                    "length": transcript.get("length"),
                    "protein_id": transcript.get("Translation", {}).get("id"),
                }
                transcripts.append(transcript_info)
            return transcripts
        return None

    def get_homologs(self, ensembl_id: str) -> Optional[Dict]:
        """Get homologs (orthologs and paralogs) for a gene."""
        url = f"{self.base_url}/homology/id/{ensembl_id}"
        params = {"format": "full"}
        response = self._make_request(url, params)

        if response and "data" in response:
            orthologs = []
            paralogs = []

            for homology in response["data"][0]["homologies"]:
                target = homology["target"]
                homolog_info = {
                    "id": target.get("id"),
                    "species": target.get("species"),
                    "protein_id": target.get("protein_id"),
                    "type": homology.get("type"),
                    "dn_ds": homology.get("dn_ds"),
                    "confidence": homology.get("is_high_confidence"),
                }

                if homology.get("type") == "ortholog_one2one":
                    orthologs.append(homolog_info)
                elif homology.get("type") in [
                    "within_species_paralog",
                    "other_paralog",
                ]:
                    paralogs.append(homolog_info)

            return {"orthologs": orthologs, "paralogs": paralogs}
        return None

    def get_protein_domains(self, protein_id: str) -> Optional[List[Dict]]:
        """Get protein domain information from Ensembl."""
        url = f"{self.base_url}/lookup/id/{protein_id}"
        params = {"expand": "1"}
        response = self._make_request(url, params)

        if response and "feature" in response:
            domains = []
            for feature in response["feature"]:
                if feature.get("type") in ["domain", "region"]:
                    domain_info = {
                        "type": feature.get("type"),
                        "description": feature.get("description"),
                        "start": feature.get("start"),
                        "end": feature.get("end"),
                        "interpro_id": feature.get("interpro"),
                    }
                    domains.append(domain_info)
            return domains
        return None


class MyGeneFetcher(BaseFetcher):
    """Fetcher for MyGene.info API."""

    def __init__(self, species: str = "human"):
        super().__init__("https://mygene.info/v3")
        self.species = species

    def get_enhanced_gene_info(self, gene_symbol: str) -> Optional[Dict]:
        """Get enhanced gene information from MyGene.info."""
        url = f"{self.base_url}/query"
        params = {
            "q": gene_symbol,
            "species": "human" if self.species == "human" else self.species,
            "fields": "entrezgene,symbol,name,alias,uniprot,hgnc,type_of_gene,map_location,summary,genomic_pos",
            "size": 1,
        }

        response = self._make_request(url, params)

        if response and "hits" in response and response["hits"]:
            hit = response["hits"][0]
            return {
                "entrez_id": hit.get("entrezgene"),
                "symbol": hit.get("symbol"),
                "name": hit.get("name"),
                "aliases": hit.get("alias", []),
                "uniprot_id": hit.get("uniprot"),
                "hgnc_id": hit.get("hgnc"),
                "type_of_gene": hit.get("type_of_gene"),
                "map_location": hit.get("map_location"),
                "summary": hit.get("summary"),
                "genomic_pos": hit.get("genomic_pos"),
            }
        return None
