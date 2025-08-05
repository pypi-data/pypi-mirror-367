from typing import List, Optional
from datetime import datetime
from beanie import Document
from pydantic import BaseModel, Field
from cpe_model import CPEMatchingCondition

class CPEEntity(BaseModel):
    entity_group: str
    word: str
    score: float
    start: int
    end: int


class ProductWithPart(BaseModel):
    name: str
    part: str
    
class CVEPredictions(BaseModel):
    cvss: Optional[float] = None
    cwes: Optional[List[str]] = None 
    cpes: List[CPEEntity] = Field(default_factory=list)
    vendors: List[str] = Field(default_factory=list)
    products: List[ProductWithPart] = Field(default_factory=list)
    versions: List[str] = Field(default_factory=list)

class CVEProcessingResults(Document):
    id: str
    cvss: float
    cwe: List[str]
    cpe: List[CPEMatchingCondition]
    predictions: CVEPredictions = Field(default_factory=CVEPredictions)
    published_date: Optional[datetime] = None
    last_modified_date: Optional[datetime] = None

    class Settings:
        name = "cve-processing-results"
        use_revision = False
        id_type = str

    class Config:
        arbitrary_types_allowed = True
