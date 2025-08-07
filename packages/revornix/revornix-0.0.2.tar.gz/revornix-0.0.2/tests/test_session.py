import os
from dotenv import load_dotenv
load_dotenv(override=True)

import revornix.schema.document as document_schema
import revornix.schema.section as section_schame
from revornix.core import Session

base_url = os.environ.get('REVORNIX_URL_PREFIX')
api_key = os.environ.get('API_KEY')

session = Session(base_url=base_url, api_key=api_key)
    
def test_create_file_document():
    data = document_schema.FileDocumentParameters(
        file_name="demo",
        sections=[],
        auto_summary=False
    )
    res = session.create_file_document(data=data)
    assert res is not None
    
def test_create_website_document():
    data = document_schema.WebsiteDocumentParameters(
        url="https://www.google.com",
        sections=[],
        auto_summary=False
    )
    res = session.create_website_document(data=data)
    assert res is not None
    
def test_create_quick_note_document():
    data = document_schema.QuickNoteDocumentParameters(
        content="test",
        sections=[],
        auto_summary=False
    )
    res = session.create_quick_note_document(data=data)
    assert res is not None
    
def test_create_document_label():
    data = document_schema.LabelAddRequest(
        name="test"
    )
    res = session.create_document_label(data=data)
    assert res is not None
    
def test_create_section_label():
    data = section_schame.LabelAddRequest(
        name="test"
    )
    res = session.create_section_label(data=data)
    assert res is not None

def test_get_mine_all_document_labels():
    res = session.get_mine_all_document_labels()
    assert res is not None