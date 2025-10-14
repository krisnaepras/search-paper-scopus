"""
Common enums used across schemas
"""

from enum import Enum


class DocumentType(str, Enum):
    """Document type filter"""
    article = "ar"
    conference = "cp"
    review = "re"
    book = "bk"
    chapter = "ch"
    note = "no"
    editorial = "ed"
    letter = "le"


class SubjectArea(str, Enum):
    """Subject area filter"""
    computer_science = "COMP"
    engineering = "ENGI"
    medicine = "MEDI"
    mathematics = "MATH"
    physics = "PHYS"
    chemistry = "CHEM"
    business = "BUSI"
    economics = "ECON"
    social_sciences = "SOCI"
    psychology = "PSYC"


class SortBy(str, Enum):
    """Sort order options"""
    relevance = "relevance"
    citations = "-citedby-count"
    date_newest = "-date"
    date_oldest = "date"


class ExportFormat(str, Enum):
    """Export format options"""
    json = "json"
    csv = "csv"
    excel = "excel"
