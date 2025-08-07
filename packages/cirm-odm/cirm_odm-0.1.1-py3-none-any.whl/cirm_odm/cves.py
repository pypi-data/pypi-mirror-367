from typing import List, Literal
from .cpe_model import CPEMatchingCondition
from beanie import Document


class CVEModel(Document):
    """
    Represents a Common Vulnerabilities and Exposures (CVE) document.

    Attributes:
        id : Unique identifier for the CVE.
        description : Detailed description of the CVE.
        status : Current status of the CVE.
        published_date : Date when the CVE was published.
        last_modified_date : Date when the CVE was last modified.
        cvss : Common Vulnerability Scoring System score.
        cwe : List of CWE IDs associated with the CVE.
        cpe : List of CPE conditions.
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
            name : Name of the MongoDB collection.
            use_revision : Flag indicating whether to use revisioning.
            id_type : Type of the document's ID field.
        """
        name = 'cves'
        use_revision = False
        id_type = str

    class Config:
        """
        Pydantic configuration for the CVEModel.

        Attributes:
            arbitrary_types_allowed : Flag indicating whether
            to allow arbitrary types.
        """
        arbitrary_types_allowed = True
