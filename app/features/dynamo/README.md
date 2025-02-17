
# Document Processing Toolkit

# Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [File Type Support](#file-type-support)
- [Usage](#usage)
- [Templates](#templates)
- [Examples](#examples)

## Overview

This toolkit provides a comprehensive suite of utilities to process and summarize various types of documents and generate educational flashcards. It leverages AI models to extract meaningful insights from documents, making it useful for educational, research, and business purposes.

## Features

- **Document Loaders**: Supports loading documents from various file formats including PDF, CSV, TXT, MD, DOCX, PPTX, XLS, XLSX, XML, URLs and IMGs.
- **Google Drive Integration**: Capable of loading documents directly from Google Drive, including Google Docs, Sheets, and Slides.
- **AI Model Integration**: Uses Google Generative AI for summarization and concept generation.
- **Text Splitting**: Efficiently splits large documents into manageable chunks for processing.
- **Error Handling**: Robust error handling for unsupported file types and file handling issues.
- **Flashcard Generation**: Generates flashcards from text summaries for educational purposes.

## Installation

Ensure you have the necessary dependencies installed:

```bash
pip install -r requirements.txt
```

## File Type Support

| File Type | Description | Function |
|-----------|-------------|----------|
| PDF       | Portable Document Format | `load_pdf_documents` |
| CSV       | Comma-Separated Values | `load_csv_documents` |
| TXT       | Plain Text | `load_txt_documents` |
| MD        | Markdown | `load_md_documents` |
| URL       | Web URL | `load_url_documents` |
| Youtube URL       | Youtube URL | `summarize_transcript_youtube_url` |
| PPTX      | PowerPoint Presentation | `load_pptx_documents` |
| DOCX      | Word Document | `load_docx_documents` |
| XLS       | Excel Spreadsheet | `load_xls_documents` |
| XLSX      | Excel Spreadsheet | `load_xlsx_documents` |
| XML       | XML Document | `load_xml_documents` |
| Google Docs | Documents from Google Drive | `load_gdocs_documents` |
| Google Sheets | Spreadsheets from Google Drive | `load_gsheets_documents` |
| Google Slides | Presentations from Google Drive | `load_gslides_documents` |
| Google PDFs | PDFs from Google Drive | `load_gpdf_documents` |
| Images | PNG, JPG, JPEG | `generate_concepts_from_img` |

## Usage

### Document Loading

Load documents from various sources using the provided functions:

#### PDF Documents

```python
load_pdf_documents(pdf_url: str, verbose=False)
```

#### CSV Documents

```python
load_csv_documents(csv_url: str, verbose=False)
```

#### TXT Documents

```python
load_txt_documents(notes_url: str, verbose=False)
```

#### Markdown Documents

```python
load_md_documents(notes_url: str, verbose=False)
```

#### URL Documents

```python
load_url_documents(url: str, verbose=False)
```

#### PowerPoint Documents

```python
load_pptx_documents(pptx_url: str, verbose=False)
```

#### Word Documents

```python
load_docx_documents(docx_url: str, verbose=False)
```

#### Excel Documents (XLS)

```python
load_xls_documents(xls_url: str, verbose=False)
```

#### Excel Documents (XLSX)

```python
load_xlsx_documents(xlsx_url: str, verbose=False)
```

#### XML Documents

```python
load_xml_documents(xml_url: str, verbose=False)
```

#### Google Docs

```python
load_gdocs_documents(drive_folder_url: str, verbose=False)
```

#### Google Sheets

```python
load_gsheets_documents(drive_folder_url: str, verbose=False)
```

#### Google Slides

```python
load_gslides_documents(drive_folder_url: str, verbose=False)
```

#### Google PDFs

```python
load_gpdf_documents(drive_folder_url: str, verbose=False)
```

#### Images
```python
generate_concepts_from_img(img_url: str)
```

# Templates
## Request template
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "string"
      },
      {
        "name": "file_type",
        "value": "string"
      },
      {
        "name": "lang",
        "value": "string"
      }
    ]
  }
}
```

# Examples

## Youtube URL
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://www.youtube.com/watch?v=YFPIP9NxU30"
      },
      {
        "name": "file_type",
        "value": "youtube_url"
      }
    ]
  }
}
```
## PDF File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
      },
      {
        "name": "file_type",
        "value": "pdf"
      }
    ]
  }
}
```
## CSV File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv"
      },
      {
        "name": "file_type",
        "value": "csv"
      }
    ]
  }
}
```
## TXT File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/openai.txt"
      },
      {
        "name": "file_type",
        "value": "txt"
      }
    ]
  }
}
```
## MD File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://raw.githubusercontent.com/radicalxdev/kai-ai-backend/main/README.md"
      },
      {
        "name": "file_type",
        "value": "md"
      }
    ]
  }
}
```
## URL File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://en.wikipedia.org/wiki/Massachusetts_Institute_of_Technology"
      },
      {
        "name": "file_type",
        "value": "url"
      }
    ]
  }
}
```
## PPTX File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx"
      },
      {
        "name": "file_type",
        "value": "pptx"
      }
    ]
  }
}
```
## DOCX File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://calibre-ebook.com/downloads/demos/demo.docx"
      },
      {
        "name": "file_type",
        "value": "docx"
      }
    ]
  }
}
```
## XLS File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://www.cmu.edu/blackboard/files/evaluate/tests-example.xls"
      },
      {
        "name": "file_type",
        "value": "xls"
      }
    ]
  }
}
```
## XLSX File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://github.com/AaronSosaRamos/mission-flights/raw/main/files-for-test/Free_Test_Data_1MB_XLSX.xlsx"
      },
      {
        "name": "file_type",
        "value": "xlsx"
      }
    ]
  }
}
```
## XML File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
      },
      {
        "name": "file_type",
        "value": "xml"
      }
    ]
  }
}
```
## Google Docs File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link"
      },
      {
        "name": "file_type",
        "value": "gdoc"
      }
    ]
  }
}
```
## Google Sheet File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://docs.google.com/spreadsheets/d/15Wvok1cjrTJGQQyokVKPsJ2jW2mbiuAJ/edit?usp=drive_link"
      },
      {
        "name": "file_type",
        "value": "gsheet"
      }
    ]
  }
}
```
## Google Slide File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://docs.google.com/presentation/d/1m99qIFwnGXIoxCJNCmIbecIvnoP3ecbT/edit?usp=drive_link"
      },
      {
        "name": "file_type",
        "value": "gslide"
      }
    ]
  }
}
```
## Google PDF File
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://drive.google.com/file/d/1JIZxgX4aLUUl5bHy5SE8OK7Eg9tT1ZkA/view?usp=drive_link"
      },
      {
        "name": "file_type",
        "value": "gpdf"
      }
    ]
  }
}
```
## Image File (PNG, JPG, JPEG)
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": 1,
    "inputs": [
      {
        "name": "file_url",
        "value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2023/02/13/adverse_1-1024x546.png"
      },
      {
        "name": "file_type",
        "value": "img"
      }
    ]
  }
}
```