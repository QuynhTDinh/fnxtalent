"""
FNX Competency Taxonomy — Single Source of Truth.

This module provides the canonical competency framework that all agents,
prompts, and UI components reference. Do NOT hardcode competency definitions
elsewhere; always import from here.
"""

from .loader import TaxonomyLoader, get_taxonomy

__all__ = ["TaxonomyLoader", "get_taxonomy"]
