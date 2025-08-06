"""
pdfnaut is a Python library for reading and writing PDFs.
"""

from __future__ import annotations

from .cos import PdfParser, PdfSerializer, PdfTokenizer
from .document import PdfDocument

__all__ = ("PdfParser", "PdfTokenizer", "PdfSerializer", "PdfDocument")

__name__ = "pdfnaut"
__version__ = "0.10.0"
__description__ = "Explore PDFs with ease"
__license__ = "Apache-2.0"
