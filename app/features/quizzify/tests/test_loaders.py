import pytest
from unittest.mock import patch, MagicMock
from app.services.tool_registry import ToolFile
from app.features.quizzify.tools import URLLoader, BytesFilePDFLoader, Document  # Adjust the import path as necessary

@pytest.fixture
def pdf_loader():
    return BytesFilePDFLoader

@pytest.fixture
def url_loader(pdf_loader):
    return URLLoader(file_loader=pdf_loader, expected_file_type="pdf")

@patch('requests.get')
def test_load_pdf_from_url(mock_get, url_loader):
    
    pdf_file_path = "features/quizzify/tests/test.pdf"
    
    with open(pdf_file_path, 'rb') as file:
        mock_pdf_content = file.read()
    
    # Mocking the response of requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = mock_pdf_content
    mock_get.return_value = mock_response

    # The URL you're testing with (doesn't matter in this case since it's mocked)
    test_url = "https://example.com/test.pdf"

    # Assuming your Document class has a simple structure for this example
    expected_document = Document(page_content="Mock PDF Content", metadata={"source": "pdf", "page_number": 1})

    # Run the loader
    documents = url_loader.load([test_url])

    # Verify the results
    assert isinstance(documents, list)
    assert len(documents) == 1

@patch('requests.get')
def test_load_pdf_from_url(mock_get):
    # Simulate reading a local PDF file or use mock PDF content
    pdf_file_path = "features/quizzify/tests/test.pdf"
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_content = pdf_file.read()

    # Mocking the response of requests.get to simulate downloading the PDF
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = pdf_content
    mock_get.return_value = mock_response

    # The specific URL you want to test with
    test_url = "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
    tool_file = ToolFile(url=test_url, filePath = None, filename = None)
    
    # Instantiate URLLoader class 
    url_loader_instance = URLLoader(BytesFilePDFLoader, expected_file_type="pdf")

    # Assuming you have a URL loader or similar functionality in your application
    documents = url_loader_instance.load([tool_file])
    
    # Verify the results
    assert isinstance(documents, list)
    assert len(documents) == 1