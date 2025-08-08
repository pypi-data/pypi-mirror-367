"""
GeneInfo: A Python package for comprehensive gene information retrieval.

This package provides functionality to fetch detailed gene information including:
- Basic gene information and transcripts
- Protein domains
- Gene ontology terms
- Pathways
- Protein-protein interactions
- Paralogs and orthologs
- Clinical variants (ClinVar)
- Cancer mutations (COSMIC)
"""

__version__ = "0.1.0"
__author__ = "Chunjie Liu"

from .core import GeneInfo
from .fetchers import EnsemblFetcher, GOFetcher, ReactomeFetcher, UniProtFetcher
from .utils import get_api_key, get_email, load_environment

__all__ = [
    "GeneInfo",
    "EnsemblFetcher",
    "UniProtFetcher",
    "GOFetcher",
    "ReactomeFetcher",
]
