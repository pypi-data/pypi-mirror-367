"""
Data fetchers for various biological databases.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
import urllib3
from Bio import Entrez

from .mock_data import MOCK_GENE_DATA

# Suppress SSL warnings for STRING-db
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class BaseFetcher:
    """Base class for API fetchers with rate limiting and error handling."""

    def __init__(
        self, base_url: str, rate_limit: float = 0.1, use_mock: bool = False
    ):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.use_mock = use_mock
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "GeneInfo/0.1.0 (https://github.com/chunjie-sam-liu/geneinfo)"
            }
        )

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with rate limiting and error handling."""
        if self.use_mock:
            return None  # Let individual fetchers handle mock data

        try:
            time.sleep(self.rate_limit)  # Rate limiting
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Handle different content types
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            else:
                return {"content": response.text}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return None


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

    def _get_mock_protein_domains(
        self, protein_id: str
    ) -> Optional[List[Dict]]:
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


class UniProtFetcher(BaseFetcher):
    """Fetcher for UniProt API."""

    def __init__(self, use_mock: bool = None):
        super().__init__("https://rest.uniprot.org", use_mock=use_mock)

        # Auto-detect if we should use mock data
        if use_mock is None:
            self.use_mock = self._should_use_mock()

    def _should_use_mock(self) -> bool:
        """Check if external API is accessible."""
        try:
            response = self.session.get(
                f"{self.base_url}/uniprotkb/search?query=P53_HUMAN&size=1",
                timeout=5,
            )
            return response.status_code != 200
        except Exception:
            return True

    def get_protein_domains(self, protein_id: str) -> Optional[List[Dict]]:
        """Get protein domain information from UniProt."""
        if self.use_mock:
            return self._get_mock_domains(protein_id)

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

    def _get_mock_domains(self, protein_id: str) -> Optional[List[Dict]]:
        """Get mock protein domain information."""
        for mock_gene, data in MOCK_GENE_DATA.items():
            for transcript in data["transcripts"]:
                if transcript.get("protein_id") == protein_id:
                    return data["protein_domains"]
            # Also check if the gene symbol matches
            if (
                data["basic_info"].get("external_name", "").upper()
                == protein_id.upper()
            ):
                return data["protein_domains"]
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


class ClinVarFetcher(BaseFetcher):
    """Fetcher for ClinVar clinical variants using NCBI Entrez."""

    def __init__(self, email: str, use_mock: bool = None):
        super().__init__("https://eutils.ncbi.nlm.nih.gov", use_mock=use_mock)
        self.email = email
        Entrez.email = email

        # Auto-detect if we should use mock data
        if use_mock is None:
            self.use_mock = self._should_use_mock()

    def _should_use_mock(self) -> bool:
        """Check if external API is accessible."""
        try:
            # Test with a simple search
            handle = Entrez.esearch(db="clinvar", term="BRCA1[gene]", retmax=1)
            record = Entrez.read(handle)
            return len(record.get("IdList", [])) == 0
        except Exception:
            return True

    def get_clinical_variants(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get clinical variants from ClinVar for a gene."""
        if self.use_mock:
            return self._get_mock_clinical_variants(gene_symbol)

        try:
            # Search ClinVar for variants in the gene
            search_term = f"{gene_symbol}[gene]"
            handle = Entrez.esearch(db="clinvar", term=search_term, retmax=100)
            search_results = Entrez.read(handle)
            handle.close()

            ids = search_results.get("IdList", [])
            if not ids:
                return None

            # Fetch detailed information for the variants
            handle = Entrez.efetch(
                db="clinvar", id=ids[:20], rettype="xml"
            )  # Limit to 20 for performance
            xml_data = handle.read()
            handle.close()

            # Parse the XML data (simplified parsing)
            variants = []
            if xml_data:
                # For now, return basic info since XML parsing is complex
                for i, variant_id in enumerate(ids[:20]):
                    variant_info = {
                        "variant_id": variant_id,
                        "gene": gene_symbol,
                        "database": "ClinVar",
                        "url": f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{variant_id}/",
                        "clinical_significance": "Unknown",  # Would need XML parsing for details
                        "condition": "Unknown",
                    }
                    variants.append(variant_info)

            return variants if variants else None

        except Exception as e:
            logger.error(
                f"Error fetching ClinVar data for {gene_symbol}: {str(e)}"
            )
            return None

    def _get_mock_clinical_variants(
        self, gene_symbol: str
    ) -> Optional[List[Dict]]:
        """Get mock clinical variants."""
        gene_key = gene_symbol.upper()
        for mock_gene, data in MOCK_GENE_DATA.items():
            if (
                mock_gene == gene_key
                or data["basic_info"].get("external_name", "").upper()
                == gene_key
                or data["basic_info"].get("display_name", "").upper()
                == gene_key
            ):
                return data.get("clinical_variants", [])
        return None


class StringDBFetcher(BaseFetcher):
    """Fetcher for STRING-db protein-protein interactions."""

    def __init__(self, species: str = "9606", use_mock: bool = None):
        # Use HTTPS with SSL verification disabled due to certificate issues
        super().__init__("https://string-db.org/api", use_mock=use_mock)
        self.species = species  # NCBI taxon ID (9606 for human)

        # Disable SSL verification for STRING-db due to certificate issues
        self.session.verify = False

        # Auto-detect if we should use mock data
        if use_mock is None:
            self.use_mock = self._should_use_mock()

    def _should_use_mock(self) -> bool:
        """Check if external API is accessible."""
        try:
            response = self.session.get(
                f"{self.base_url}/json/version", timeout=10
            )
            return response.status_code != 200
        except Exception:
            return True

    def get_protein_interactions(
        self, gene_symbol: str
    ) -> Optional[List[Dict]]:
        """Get protein-protein interactions from STRING-db."""
        if self.use_mock:
            return self._get_mock_interactions(gene_symbol)

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

    def _get_mock_interactions(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get mock protein interactions."""
        gene_key = gene_symbol.upper()
        for mock_gene, data in MOCK_GENE_DATA.items():
            if (
                mock_gene == gene_key
                or data["basic_info"].get("external_name", "").upper()
                == gene_key
                or data["basic_info"].get("display_name", "").upper()
                == gene_key
            ):
                return data.get("protein_interactions", [])
        return None


class GwasFetcher(BaseFetcher):
    """Fetches GWAS data from EBI GWAS Catalog."""

    def __init__(self):
        super().__init__("https://www.ebi.ac.uk/gwas/rest/api")
        self.logger = logging.getLogger(__name__)

    def get_gwas_data(self, gene_name: str) -> Dict[str, Any]:
        """Get GWAS associations for a gene."""
        try:
            # Find SNPs associated with the gene
            snps_url = f"{self.base_url}/singleNucleotidePolymorphisms/search/findByGene"
            snps_response = self._make_request(
                snps_url, params={"geneName": gene_name}
            )

            if not snps_response or "_embedded" not in snps_response:
                return {}

            snps = snps_response["_embedded"]["singleNucleotidePolymorphisms"]
            associations = []

            # Get associations for each SNP (limit to top 10 SNPs to avoid too many requests)
            for snp in snps[:10]:
                rs_id = snp["rsId"]
                assoc_url = f"{self.base_url}/singleNucleotidePolymorphisms/{rs_id}/associations"
                assoc_response = self._make_request(assoc_url)

                if assoc_response and "_embedded" in assoc_response:
                    snp_associations = assoc_response["_embedded"][
                        "associations"
                    ]

                    for assoc in snp_associations:
                        # Get EFO traits for this association
                        traits_url = assoc["_links"]["efoTraits"]["href"]
                        traits_response = self._make_request(traits_url)

                        if traits_response and "_embedded" in traits_response:
                            traits = traits_response["_embedded"]["efoTraits"]

                            associations.append(
                                {
                                    "rsId": rs_id,
                                    "pvalue": assoc.get("pvalue"),
                                    "pvalueExponent": assoc.get(
                                        "pvalueExponent"
                                    ),
                                    "betaNum": assoc.get("betaNum"),
                                    "betaDirection": assoc.get("betaDirection"),
                                    "riskFrequency": assoc.get("riskFrequency"),
                                    "traits": [
                                        {
                                            "trait": trait["trait"],
                                            "uri": trait["uri"],
                                        }
                                        for trait in traits
                                    ],
                                }
                            )

            return {
                "associations": associations,
                "total_snps": len(snps),
                "analyzed_snps": min(10, len(snps)),
            }

        except Exception as e:
            self.logger.error(f"Error fetching GWAS data for {gene_name}: {e}")
            return {}


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
            import ssl

            import mygene

            # Create SSL context that doesn't verify certificates (for development)
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


class OMIMFetcher(BaseFetcher):
    """Fetches phenotype and disease data from OMIM API."""

    def __init__(self, api_key: str = "4BO6qzmbRtSUfUS97syQPw"):
        super().__init__("https://api.omim.org/api")
        self.api_key = api_key
        self.session.headers.update({"ApiKey": self.api_key})

    def get_phenotype_data(self, gene_symbol: str) -> Dict[str, Any]:
        """Get phenotype and disease associations from OMIM."""
        try:
            # First search for gene entries
            search_url = f"{self.base_url}/entry/search"
            search_params = {
                "search": f"{gene_symbol}[gene symbol]",
                "include": "geneMap",
                "limit": 10,
                "format": "json",
            }

            search_result = self._make_request(search_url, search_params)

            if not search_result or "omim" not in search_result:
                return {}

            phenotypes = []
            gene_entries = []

            # Process search results
            if "searchResponse" in search_result["omim"]:
                search_response = search_result["omim"]["searchResponse"]
                if "entryList" in search_response:
                    for entry in search_response["entryList"]:
                        entry_data = entry.get("entry", {})
                        mim_number = entry_data.get("mimNumber")

                        if mim_number:
                            gene_entries.append(
                                {
                                    "mim_number": mim_number,
                                    "title": entry_data.get("titles", {}).get(
                                        "preferredTitle", ""
                                    ),
                                    "prefix": entry_data.get("prefix", ""),
                                }
                            )

                            # Check for phenotype map in gene map
                            if "geneMapList" in entry_data:
                                for gene_map in entry_data["geneMapList"]:
                                    if "phenotypeMapList" in gene_map:
                                        for phenotype_map in gene_map[
                                            "phenotypeMapList"
                                        ]:
                                            phenotype_info = {
                                                "phenotype": phenotype_map.get(
                                                    "phenotype"
                                                ),
                                                "phenotype_mim_number": phenotype_map.get(
                                                    "phenotypeMimNumber"
                                                ),
                                                "inheritance": phenotype_map.get(
                                                    "phenotypeInheritance"
                                                ),
                                                "mapping_key": phenotype_map.get(
                                                    "phenotypeMappingKey"
                                                ),
                                                "gene_mim_number": mim_number,
                                                "chromosome": gene_map.get(
                                                    "chromosomeSymbol"
                                                ),
                                                "cytolocation": gene_map.get(
                                                    "cytoLocation"
                                                ),
                                            }
                                            phenotypes.append(phenotype_info)

            # Get detailed information for gene entries
            detailed_phenotypes = []
            for gene_entry in gene_entries[:3]:  # Limit to top 3 results
                mim_number = gene_entry["mim_number"]
                detailed_data = self._get_detailed_entry(mim_number)
                if detailed_data:
                    detailed_phenotypes.extend(
                        self._extract_phenotypes_from_entry(
                            detailed_data, mim_number
                        )
                    )

            # Combine and deduplicate phenotypes
            all_phenotypes = phenotypes + detailed_phenotypes
            unique_phenotypes = []
            seen_phenotypes = set()

            for pheno in all_phenotypes:
                phenotype_key = (
                    pheno.get("phenotype", ""),
                    pheno.get("phenotype_mim_number"),
                )
                if phenotype_key not in seen_phenotypes and pheno.get(
                    "phenotype"
                ):
                    seen_phenotypes.add(phenotype_key)
                    unique_phenotypes.append(pheno)

            return {
                "gene_entries": gene_entries,
                "phenotypes": unique_phenotypes[
                    :20
                ],  # Limit to top 20 phenotypes
                "total_phenotypes": len(unique_phenotypes),
            }

        except Exception as e:
            self.logger.error(
                f"Error fetching OMIM data for {gene_symbol}: {e}"
            )
            return {}

    def _get_detailed_entry(self, mim_number: str) -> Optional[Dict]:
        """Get detailed entry information from OMIM."""
        try:
            url = f"{self.base_url}/entry"
            params = {
                "mimNumber": mim_number,
                "include": "geneMap,text:phenotype,text:clinicalFeatures",
                "format": "json",
            }

            result = self._make_request(url, params)
            if result and "omim" in result and "entryList" in result["omim"]:
                entries = result["omim"]["entryList"]
                if entries and len(entries) > 0:
                    return entries[0].get("entry")

            return None

        except Exception as e:
            self.logger.error(
                f"Error fetching detailed OMIM entry {mim_number}: {e}"
            )
            return None

    def _extract_phenotypes_from_entry(
        self, entry: Dict, mim_number: str
    ) -> List[Dict]:
        """Extract phenotype information from detailed entry."""
        phenotypes = []

        # Extract from gene map
        if "geneMapList" in entry:
            for gene_map in entry["geneMapList"]:
                if "phenotypeMapList" in gene_map:
                    for phenotype_map in gene_map["phenotypeMapList"]:
                        phenotype_info = {
                            "phenotype": phenotype_map.get("phenotype"),
                            "phenotype_mim_number": phenotype_map.get(
                                "phenotypeMimNumber"
                            ),
                            "inheritance": phenotype_map.get(
                                "phenotypeInheritance"
                            ),
                            "mapping_key": phenotype_map.get(
                                "phenotypeMappingKey"
                            ),
                            "gene_mim_number": mim_number,
                            "chromosome": gene_map.get("chromosomeSymbol"),
                            "cytolocation": gene_map.get("cytoLocation"),
                        }
                        phenotypes.append(phenotype_info)

        return phenotypes
