from pydantic import BaseModel

class LabelAddRequest(BaseModel):
    name: str
    
class BaseSectionInfo(BaseModel):
    id: int
    title: str
    description: str
        
class AllMySectionsResponse(BaseModel):
    data: list[BaseSectionInfo]