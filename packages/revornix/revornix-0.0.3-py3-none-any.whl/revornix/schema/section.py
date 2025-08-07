from pydantic import BaseModel

class LabelAddRequest(BaseModel):
    name: str
    
class BaseSectionInfo(BaseModel):
    id: int
    title: str
    description: str
        
class AllMySectionsResponse(BaseModel):
    data: list[BaseSectionInfo]
    
class SectionCreateRequest(BaseModel):
    title: str
    description: str
    public: bool
    cover_id: int | None = None
    labels: list[int]
    
class SectionCreateResponse(BaseModel):
    id: int