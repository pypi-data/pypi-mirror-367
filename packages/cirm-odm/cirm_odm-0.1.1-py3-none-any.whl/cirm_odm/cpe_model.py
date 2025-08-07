from typing import List, Optional, Literal
from pydantic import BaseModel


class CPEModel(BaseModel):
    """
    Represents a Common Platform Enumeration (CPE) string.

    Attributes:
        part : The part of the CPE (e.g., 'a' for application).
        vendor : The vendor name.
        product : The product name.
        version : The product version.
        update : The update version.
        edition : The edition of the product.
        language : The language of the product.
        sw_edition : The software edition.
        target_sw : The target software.
        target_hw : The target hardware.
        other : Other information.
        raw : The raw CPE string.
    """
    part: str
    vendor: str
    product: str
    version: str
    update: str
    edition: str
    language: str
    sw_edition: str
    target_sw: str
    target_hw: str
    other: str
    raw: str


class CPEMatch(BaseModel):
    """
    Represents a match for a CPE string.

    Attributes:
        cpe : The CPE model.
        vulnerable : Whether the CPE is vulnerable.
        version_start_including : The starting version, inclusive.
        version_start_excluding : The starting version, exclusive.
        version_end_excluding : The ending version, exclusive.
        version_end_including : The ending version, inclusive.
    """
    cpe: CPEModel
    vulnerable: bool
    version_start_including: Optional[str] = None
    version_start_excluding: Optional[str] = None
    version_end_excluding: Optional[str] = None
    version_end_including: Optional[str] = None


class CPEMatchingCondition(BaseModel):
    """
    Represents a condition for matching CPE strings.

    Attributes:
        cpe_match : The list of CPE matches.
        children : The child conditions.
        operator : The operator to combine conditions.
        negate : Whether to negate the condition.
    """
    cpe_match: List[CPEMatch]
    children: Optional[List["CPEMatchingCondition"]] = None
    operator: Literal['AND', 'OR']
    negate: bool
