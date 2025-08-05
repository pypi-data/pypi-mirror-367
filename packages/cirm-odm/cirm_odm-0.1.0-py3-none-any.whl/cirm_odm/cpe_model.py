from typing import List, Optional, Literal
from pydantic import BaseModel

class CPEModel(BaseModel):
    """
    Represents a Common Platform Enumeration (CPE) string.

    Attributes:
        part (str): The part of the CPE (e.g., 'a' for application).
        vendor (str): The vendor name.
        product (str): The product name.
        version (str): The product version.
        update (str): The update version.
        edition (str): The edition of the product.
        language (str): The language of the product.
        sw_edition (str): The software edition.
        target_sw (str): The target software.
        target_hw (str): The target hardware.
        other (str): Other information.
        raw (str): The raw CPE string.
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
        cpe (CPEModel): The CPE model.
        vulnerable (bool): Whether the CPE is vulnerable.
        version_start_including (Optional[str]): The starting version, inclusive.
        version_start_excluding (Optional[str]): The starting version, exclusive.
        version_end_excluding (Optional[str]): The ending version, exclusive.
        version_end_including (Optional[str]): The ending version, inclusive.
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
        cpe_match (List[CPEMatch]): The list of CPE matches.
        children (Optional[List["CPEMatchingCondition"]]): The child matching conditions.
        operator (Literal['AND', 'OR']): The operator to combine conditions.
        negate (bool): Whether to negate the condition.
    """
    cpe_match: List[CPEMatch]
    children: Optional[List["CPEMatchingCondition"]] = None  
    operator: Literal['AND', 'OR']
    negate: bool
