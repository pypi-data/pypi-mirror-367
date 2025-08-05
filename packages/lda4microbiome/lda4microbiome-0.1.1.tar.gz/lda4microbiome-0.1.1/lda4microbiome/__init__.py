"""
LDA4Microbiome: A comprehensive workflow for LDA analysis of microbiome data using MALLET

This package provides tools for:
- Taxonomic data preprocessing
- LDA model training with MALLET
- Model selection and evaluation
- Results visualization and analysis
"""

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main classes for easy access
from .preprocessing import TaxonomyProcessor
from .training import LDATrainer  
from .selection import SankeyDataProcessor
from .visualization import LDAModelVisualizer, TopicFeatureProcessor, MCComparison

__all__ = [
    'TaxonomyProcessor',
    'LDATrainer', 
    'SankeyDataProcessor',
    'LDAModelVisualizer',
    'TopicFeatureProcessor',
    'MCComparison'
]

