import httpx
from revornix.api.document import DocumentApi
from revornix.api.section import SectionApi
from revornix.schema.document import FileDocumentParameters, WebsiteDocumentParameters, QuickNoteDocumentParameters, DocumentCreateResponse, CreateLabelResponse, LabelAddRequest, LabelListResponse

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
        
    def create_file_document(self, data: FileDocumentParameters) -> DocumentCreateResponse:
        payload = data.model_dump()
        payload["category"] = 0
        payload["from_plat"] = self.from_plat
        response = self.httpx_client.post(DocumentApi.create_document, json=payload)
        response.raise_for_status()
        return DocumentCreateResponse.model_validate(response.json())

    def create_website_document(self, data: WebsiteDocumentParameters) -> DocumentCreateResponse:
        payload = data.model_dump()
        payload["category"] = 1
        payload["from_plat"] = self.from_plat
        response = self.httpx_client.post(DocumentApi.create_document, json=payload)
        response.raise_for_status()
        return DocumentCreateResponse.model_validate(response.json())

    def create_quick_note_document(self, data: QuickNoteDocumentParameters) -> DocumentCreateResponse:
        payload = data.model_dump()
        payload["category"] = 2
        payload["from_plat"] = self.from_plat
        response = self.httpx_client.post(DocumentApi.create_document, json=payload)
        response.raise_for_status()
        return DocumentCreateResponse.model_validate(response.json())

    def get_mine_all_document_labels(self) -> LabelListResponse:
        response = self.httpx_client.post(DocumentApi.get_mine_all_document_labels)
        response.raise_for_status()
        return LabelListResponse.model_validate(response.json())

    def create_document_label(self, data: LabelAddRequest) -> CreateLabelResponse:
        response = self.httpx_client.post(DocumentApi.create_document_label, json=data.model_dump())
        response.raise_for_status()
        return CreateLabelResponse.model_validate(response.json())

    def create_section_label(self, data: LabelAddRequest) -> CreateLabelResponse:
        response = self.httpx_client.post(SectionApi.create_section_label, json=data.model_dump())
        response.raise_for_status()
        return CreateLabelResponse.model_validate(response.json())