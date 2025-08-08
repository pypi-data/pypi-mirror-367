import httpx
from revornix.api.document import DocumentApi
from revornix.api.section import SectionApi
import revornix.schema.document as documentSchema
import revornix.schema.section as sectionSchema

class Session:
    
    api_key: str
    base_url: str
    from_plat: str = "revornix python package"
    httpx_client: httpx.AsyncClient | None = None
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.httpx_client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Api-Key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=15.0
        )
        
    def create_file_document(self, data: documentSchema.FileDocumentParameters) -> documentSchema.DocumentCreateResponse:
        payload = data.model_dump()
        payload["category"] = 0
        payload["from_plat"] = self.from_plat
        response = self.httpx_client.post(DocumentApi.create_document, json=payload)
        response.raise_for_status()
        return documentSchema.DocumentCreateResponse.model_validate(response.json())

    def create_website_document(self, data: documentSchema.WebsiteDocumentParameters) -> documentSchema.DocumentCreateResponse:
        payload = data.model_dump()
        payload["category"] = 1
        payload["from_plat"] = self.from_plat
        response = self.httpx_client.post(DocumentApi.create_document, json=payload)
        response.raise_for_status()
        return documentSchema.DocumentCreateResponse.model_validate(response.json())

    def create_quick_note_document(self, data: documentSchema.QuickNoteDocumentParameters) -> documentSchema.DocumentCreateResponse:
        payload = data.model_dump()
        payload["category"] = 2
        payload["from_plat"] = self.from_plat
        response = self.httpx_client.post(DocumentApi.create_document, json=payload)
        response.raise_for_status()
        return documentSchema.DocumentCreateResponse.model_validate(response.json())

    def get_mine_all_document_labels(self) -> documentSchema.LabelListResponse:
        response = self.httpx_client.post(DocumentApi.get_mine_all_document_labels)
        response.raise_for_status()
        return documentSchema.LabelListResponse.model_validate(response.json())

    def create_document_label(self, data: documentSchema.LabelAddRequest) -> documentSchema.CreateLabelResponse:
        response = self.httpx_client.post(DocumentApi.create_document_label, json=data.model_dump())
        response.raise_for_status()
        return documentSchema.CreateLabelResponse.model_validate(response.json())

    def create_section_label(self, data: documentSchema.LabelAddRequest) -> documentSchema.CreateLabelResponse:
        response = self.httpx_client.post(SectionApi.create_section_label, json=data.model_dump())
        response.raise_for_status()
        return documentSchema.CreateLabelResponse.model_validate(response.json())
    
    def create_section(self, data: sectionSchema.SectionCreateRequest) -> sectionSchema.SectionCreateResponse:
        response = self.httpx_client.post(SectionApi.create_section, json=data.model_dump())
        response.raise_for_status()
        return sectionSchema.SectionCreateResponse.model_validate(response.json())
    
    def get_mine_all_sections(self) -> sectionSchema.AllMySectionsResponse:
        response = self.httpx_client.post(SectionApi.get_mine_all_section)
        response.raise_for_status()
        return sectionSchema.AllMySectionsResponse.model_validate(response.json())