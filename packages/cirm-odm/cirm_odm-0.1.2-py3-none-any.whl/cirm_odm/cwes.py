from typing import List, Optional
from pydantic import BaseModel
from beanie import Document


class Detection(BaseModel):
    """
    Represents a detection method for a Common Weakness Enumeration (CWE).

    Attributes:
        detection_id : Unique identifier for the detection.
        method : The method used for detection.
        description : A description of the detection method.
        effectiveness : The effectiveness rating of the detection method.
    """
    detection_id: str
    method: Optional[str] = None
    description: Optional[str] = None
    effectiveness: Optional[str] = None


class CWEModel(Document):
    """
    Represents a Common Weakness Enumeration (CWE) document.

    Attributes:
        id : Unique identifier for the CWE.
        name : Name of the CWE.
        status : Current status of the CWE.
        description : A detailed description of the CWE.
        related_cwe_ids : List of IDs of related CWEs.
        detection : Detection method associated with the CWE.
        created_at : Timestamp when the CWE was created.
        last_update : Timestamp of the last update to the CWE.
    """
    id: str
    name: str
    status: str
    description: Optional[str] = None
    related_cwe_ids: List[str]
    detection: Optional[Detection] = None
    usage: Optional[str] = None
    created_at: Optional[str] = None
    last_update: Optional[str] = None

    class Settings:
        """
        Configuration settings for the CWEModel document.

        Attributes:
            name : Name of the MongoDB collection.
            use_revision : Flag indicating whether to use revisioning.
            id_type : Type of the document's ID field.
        """
        name = "cwes"
        use_revision = False
        id_type = str

    class Config:
        """
        Pydantic configuration for the CWEModel.

        Attributes:
            arbitrary_types_allowed: Flag indicating whether to allow types.
        """
        arbitrary_types_allowed = True
