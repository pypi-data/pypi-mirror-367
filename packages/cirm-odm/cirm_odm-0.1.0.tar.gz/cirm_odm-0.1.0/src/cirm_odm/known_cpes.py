from beanie import Document
from typing import Optional
from datetime import datetime

class KnownCPE(Document):
    vendor: str
    product: str

    published_date: Optional[datetime] = None
    last_modified_date: Optional[datetime] = None
    
    class Settings:
        name = "known-cpes"
