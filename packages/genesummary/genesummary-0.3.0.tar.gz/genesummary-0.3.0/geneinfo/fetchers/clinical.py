"""
Clinical data fetchers for ClinVar, GWAS, and OMIM APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Fetchers for clinical variants, GWAS data, and phenotype information
Version: 0.1
"""

import logging
from typing import Any, Dict, List, Optional

from Bio import Entrez

from .base import BaseFetcher

logger = logging.getLogger(__name__)


class ClinVarFetcher(BaseFetcher):
    """Fetcher for ClinVar clinical variants using NCBI Entrez."""

    def __init__(self, email: str, api_key: str):
        super().__init__("https://eutils.ncbi.nlm.nih.gov")
        self.email = email
        self.api_key = api_key

        if not email or not api_key:
            logger.warning("Email or API key not provided for ClinVar access")
            return

        Entrez.email = email
        Entrez.api_key = api_key

    def get_clinical_variants(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get clinical variants from ClinVar for a gene."""
        if not hasattr(self, "api_key") or not self.api_key:
            logger.warning("ClinVar API key not available, returning None")
            return None

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


class OMIMFetcher(BaseFetcher):
    """Fetches phenotype and disease data from OMIM API."""

    def __init__(self, api_key: str = ""):
        super().__init__("https://api.omim.org/api")
        self.api_key = api_key

        if not api_key:
            logger.warning("OMIM API key not provided")
            return

        self.session.headers.update({"ApiKey": self.api_key})

    def get_phenotype_data(self, gene_symbol: str) -> Dict[str, Any]:
        """Get phenotype and disease associations from OMIM."""
        if not hasattr(self, "api_key") or not self.api_key:
            logger.warning("OMIM API key not available, returning empty data")
            return {}

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
