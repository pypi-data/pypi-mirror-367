"""
OpenAI Batch Processing Library

Python library for creating and managing OpenAI batch API requests.
"""

from .batch import Batch
from .costs import Costs, ModelCosts

__version__ = "0.1.0"
__author__ = "Ollie Glass"
__email__ = "ollie@ollieglass.com"
__description__ = "Python library for creating and managing OpenAI Structured Outputs batch API calls"
__url__ = "https://github.com/ollieglass/openai-so-batch"

__all__ = ["Batch", "Costs", "ModelCosts"]