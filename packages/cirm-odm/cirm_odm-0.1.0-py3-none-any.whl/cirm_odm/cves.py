from typing import List, Literal
from cpe_model import CPEMatchingCondition
from beanie import Document

class CVEModel(Document):
    """
    Represents a Common Vulnerabilities and Exposures (CVE) document.

    Attributes:
        id (str): Unique identifier for the CVE.
        description (str): Detailed description of the CVE.
        status (Literal['Rejected', 'noRejected']): Current status of the CVE.
        published_date (str): Date when the CVE was published.
        last_modified_date (str): Date when the CVE was last modified.
        cvss (float): Common Vulnerability Scoring System score.
        cwe (List[str]): List of Common Weakness Enumeration IDs associated with the CVE.
        cpe (List[CPEMatchingCondition]): List of CPE matching conditions related to the CVE.
    """
    id: str
    description: str
    status: Literal['Rejected', 'noRejected']
    published_date: str
    last_modified_date: str
    cvss: float
    cwe: List[str]
    cpe: List[CPEMatchingCondition] 

    class Settings:
        """
        Configuration settings for the CVEModel document.

        Attributes:
            name (str): Name of the MongoDB collection.
            use_revision (bool): Flag indicating whether to use revisioning.
            id_type (type): Type of the document's ID field.
        """
        name = 'cves'
        use_revision = False  
        id_type = str

    class Config:
        """
        Pydantic configuration for the CVEModel.

        Attributes:
            arbitrary_types_allowed (bool): Flag indicating whether to allow arbitrary types.
        """
        arbitrary_types_allowed = True