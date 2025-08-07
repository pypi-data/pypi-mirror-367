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

from ..mock_data import MOCK_GENE_DATA
from .base import BaseFetcher

logger = logging.getLogger(__name__)


class EnsemblFetcher(BaseFetcher):
    """Fetcher for Ensembl REST API."""

    def __init__(self, species: str = "human", use_mock: bool = None):
        super().__init__("https://rest.ensembl.org", use_mock=use_mock)
        self.species = "homo_sapiens" if species.lower() == "human" else species
        self.session.headers.update({"Content-Type": "application/json"})

        # Auto-detect if we should use mock data
        if use_mock is None:
            self.use_mock = self._should_use_mock()

    def _should_use_mock(self) -> bool:
        """Check if external API is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/info/ping", timeout=5)
            return response.status_code != 200
        except Exception:
            return True

    def get_gene_info(self, gene_id: str) -> Optional[Dict]:
        """Get basic gene information from Ensembl."""
        if self.use_mock:
            return self._get_mock_gene_info(gene_id)

        # Try different endpoints based on input type
        if gene_id.startswith("ENSG"):
            url = f"{self.base_url}/lookup/id/{gene_id}"
        else:
            url = f"{self.base_url}/lookup/symbol/{self.species}/{gene_id}"

        params = {"expand": 1}
        result = self._make_request(url, params)

        if not result and not gene_id.startswith("ENSG"):
            # Try xrefs endpoint for gene symbols
            url = f"{self.base_url}/xrefs/symbol/{self.species}/{gene_id}"
            xrefs = self._make_request(url)
            if xrefs and isinstance(xrefs, list) and len(xrefs) > 0:
                for xref in xrefs:
                    if xref.get("type") == "gene":
                        gene_id = xref.get("id")
                        if gene_id:
                            url = f"{self.base_url}/lookup/id/{gene_id}"
                            result = self._make_request(url, {"expand": 1})
                            break

        return result

    def _get_mock_gene_info(self, gene_id: str) -> Optional[Dict]:
        """Get mock gene information when external API is not available."""
        # Normalize gene_id
        gene_key = gene_id.upper()

        # Try direct lookup first
        if gene_key in MOCK_GENE_DATA:
            return MOCK_GENE_DATA[gene_key]["basic_info"]

        # Try looking up by Ensembl ID in all entries
        for mock_gene, data in MOCK_GENE_DATA.items():
            if data["basic_info"].get("id") == gene_id:
                return data["basic_info"]

        # Try looking up by external name
        for mock_gene, data in MOCK_GENE_DATA.items():
            if data["basic_info"].get("external_name", "").upper() == gene_key:
                return data["basic_info"]

        logger.warning(f"No mock data available for gene: {gene_id}")
        return None

    def get_transcripts(self, ensembl_id: str) -> Optional[List[Dict]]:
        """Get transcript information for a gene."""
        if self.use_mock:
            return self._get_mock_transcripts(ensembl_id)

        url = f"{self.base_url}/lookup/id/{ensembl_id}"
        params = {"expand": 1}
        result = self._make_request(url, params)

        if result and "Transcript" in result:
            transcripts = []
            for transcript in result["Transcript"]:
                transcript_info = {
                    "id": transcript.get("id"),
                    "display_name": transcript.get("display_name"),
                    "biotype": transcript.get("biotype"),
                    "start": transcript.get("start"),
                    "end": transcript.get("end"),
                    "length": transcript.get("length"),
                    "protein_id": transcript.get("Translation", {}).get("id")
                    if transcript.get("Translation")
                    else None,
                }
                transcripts.append(transcript_info)
            return transcripts

        return None

    def _get_mock_transcripts(self, ensembl_id: str) -> Optional[List[Dict]]:
        """Get mock transcript information."""
        for mock_gene, data in MOCK_GENE_DATA.items():
            if (
                data["basic_info"].get("id") == ensembl_id
                or data["basic_info"].get("external_name", "").upper()
                == ensembl_id.upper()
            ):
                return data["transcripts"]
        return None

    def get_homologs(self, ensembl_id: str) -> Optional[Dict]:
        """Get orthologs and paralogs for a gene."""
        if self.use_mock:
            return self._get_mock_homologs(ensembl_id)

        # Use correct API endpoint with species parameter
        url = f"{self.base_url}/homology/id/{self.species}/{ensembl_id}"
        params = {"content-type": "application/json"}
        result = self._make_request(url, params)

        if result and "data" in result and len(result["data"]) > 0:
            homologs = {"orthologs": [], "paralogs": []}

            for data_entry in result["data"]:
                for homology in data_entry.get("homologies", []):
                    target = homology.get("target", {})
                    homolog_info = {
                        "id": target.get("id"),
                        "species": target.get("species"),
                        "protein_id": target.get("protein_id"),
                        "type": homology.get("type"),
                        "dn_ds": homology.get("dn_ds"),
                        "identity": target.get("perc_id"),
                        "taxonomy_level": homology.get("taxonomy_level"),
                    }

                    if homology.get("type") in [
                        "ortholog_one2one",
                        "ortholog_one2many",
                        "ortholog_many2many",
                    ]:
                        homologs["orthologs"].append(homolog_info)
                    elif "paralog" in homology.get("type", ""):
                        homologs["paralogs"].append(homolog_info)

            return homologs

        return None

    def _get_mock_homologs(self, ensembl_id: str) -> Optional[Dict]:
        """Get mock homolog information."""
        for mock_gene, data in MOCK_GENE_DATA.items():
            if (
                data["basic_info"].get("id") == ensembl_id
                or data["basic_info"].get("external_name", "").upper()
                == ensembl_id.upper()
            ):
                return {
                    "orthologs": data["orthologs"],
                    "paralogs": data["paralogs"],
                }
        return None

    def get_protein_domains(self, protein_id: str) -> Optional[List[Dict]]:
        """Get protein domain information via Ensembl protein features."""
        if self.use_mock:
            return self._get_mock_protein_domains(protein_id)

        url = f"{self.base_url}/overlap/translation/{protein_id}"
        params = {
            "feature": "protein_feature",
            "content-type": "application/json",
        }
        result = self._make_request(url, params)

        if result and isinstance(result, list):
            domains = []
            for feature in result:
                if feature.get("interpro"):  # Only include InterPro domains
                    domain_info = {
                        "id": feature.get("interpro"),
                        "description": feature.get("description"),
                        "start": feature.get("start"),
                        "end": feature.get("end"),
                        "source": "InterPro",
                    }
                    domains.append(domain_info)
            return domains

        return None

    def _get_mock_protein_domains(self, protein_id: str) -> Optional[List[Dict]]:
        """Get mock protein domain information."""
        for mock_gene, data in MOCK_GENE_DATA.items():
            for transcript in data["transcripts"]:
                if transcript.get("protein_id") == protein_id:
                    return data.get("protein_domains", [])
            # Also check if the gene symbol matches
            if (
                data["basic_info"].get("external_name", "").upper()
                == protein_id.upper()
            ):
                return data.get("protein_domains", [])
        return None

    def get_uniprot_mapping(self, protein_id: str) -> Optional[str]:
        """Get UniProt ID for an Ensembl protein ID using xrefs."""
        if self.use_mock:
            return None

        url = f"{self.base_url}/xrefs/id/{protein_id}"
        params = {"content-type": "application/json"}
        result = self._make_request(url, params)

        if result and isinstance(result, list):
            for xref in result:
                if xref.get("dbname") == "Uniprot/SWISSPROT":
                    return xref.get("primary_id")
        return None


class MyGeneFetcher(BaseFetcher):
    """Fetches enhanced gene information using mygene package."""

    def __init__(self, species: str = "human"):
        super().__init__("https://mygene.info/v3")
        self.species = (
            "human" if species.lower() in ["human", "homo_sapiens"] else species
        )
        self.logger = logging.getLogger(__name__)

        # Import mygene here to avoid import errors if not installed
        try:
            import mygene

            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            self.mg = mygene.MyGeneInfo()
            # Set SSL context for mygene if possible
            if hasattr(self.mg, "_session"):
                self.mg._session.verify = False
        except ImportError:
            self.logger.error(
                "mygene package not installed. Run: pip install mygene"
            )
            self.mg = None
        except Exception as e:
            self.logger.warning(f"SSL configuration warning: {e}")
            try:
                import mygene

                self.mg = mygene.MyGeneInfo()
            except Exception:
                self.mg = None

    def get_enhanced_gene_info(self, gene_symbol: str) -> Optional[Dict]:
        """Get enhanced gene information using MyGene.info API."""
        if not self.mg:
            return None

        try:
            # Query using gene symbol for human
            result = self.mg.query(gene_symbol, species="human", size=1)

            if not result or "hits" not in result or len(result["hits"]) == 0:
                return None

            hit = result["hits"][0]

            # Get detailed information for the gene
            gene_id = hit.get("_id")
            if gene_id:
                detailed = self.mg.getgene(
                    gene_id, fields="all", species="human"
                )
                if detailed:
                    return self._parse_mygene_data(detailed)

            return self._parse_mygene_data(hit)

        except Exception as e:
            self.logger.error(
                f"Error fetching MyGene data for {gene_symbol}: {e}"
            )
            return None

    def _parse_mygene_data(self, data: Dict) -> Dict:
        """Parse MyGene.info data into standardized format."""
        parsed = {
            "entrez_id": data.get("_id"),
            "ensembl_id": data.get("ensembl", {}).get("gene")
            if isinstance(data.get("ensembl"), dict)
            else None,
            "gene_symbol": data.get("symbol"),
            "gene_name": data.get("name"),
            "aliases": [],
            "hgnc_id": None,
            "uniprot_id": None,
            "genomic_pos": {},
            "type_of_gene": data.get("type_of_gene"),
            "map_location": data.get("map_location"),
            "summary": data.get("summary"),
        }

        # Parse aliases
        if "alias" in data:
            if isinstance(data["alias"], list):
                parsed["aliases"] = data["alias"]
            else:
                parsed["aliases"] = [data["alias"]]

        # Parse HGNC information
        if "HGNC" in data:
            parsed["hgnc_id"] = data["HGNC"]

        # Parse UniProt information
        if "uniprot" in data:
            uniprot_data = data["uniprot"]
            if isinstance(uniprot_data, dict):
                parsed["uniprot_id"] = uniprot_data.get("Swiss-Prot")
            elif isinstance(uniprot_data, str):
                parsed["uniprot_id"] = uniprot_data

        # Parse genomic position
        if "genomic_pos" in data and isinstance(data["genomic_pos"], dict):
            parsed["genomic_pos"] = {
                "chr": data["genomic_pos"].get("chr"),
                "start": data["genomic_pos"].get("start"),
                "end": data["genomic_pos"].get("end"),
                "strand": data["genomic_pos"].get("strand"),
            }
        elif "genomic_pos_hg19" in data and isinstance(
            data["genomic_pos_hg19"], dict
        ):
            parsed["genomic_pos"] = {
                "chr": data["genomic_pos_hg19"].get("chr"),
                "start": data["genomic_pos_hg19"].get("start"),
                "end": data["genomic_pos_hg19"].get("end"),
                "strand": data["genomic_pos_hg19"].get("strand"),
            }

        return parsed
