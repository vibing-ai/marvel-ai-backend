
# Syllabus Generator Toolkit

## Overview

This toolkit provides a comprehensive suite of utilities to generate syllabi from various types of educational materials. It leverages AI models to automate the creation of syllabi, making it useful for educators to streamline their course planning process.

## Features

- **Document Loaders**: Supports loading documents from various file formats including PDF, CSV, TXT, MD, DOCX, PPTX, XLS, XLSX, XML, URLs, and images.
- **Google Drive Integration**: Capable of loading documents directly from Google Drive, including Google Docs, Sheets, and Slides.
- **AI Model Integration**: Uses AI models for extracting and organizing educational content.
- **Error Handling**: Robust error handling for unsupported file types and file handling issues.
- **Syllabus Generation**: Generates detailed syllabi from provided documents and metadata.

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

# Request Templates

## Youtube URL
```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "Linear Regression"
      },
      {
        "name": "instructor_name",
        "value": "Wilfredo Sosa"
      },
      {
        "name": "instructor_title",
        "value": "Master in CS"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
      {
        "name": "file_url",
        "value": "https://www.youtube.com/watch?v=YUPagM-OB_M"
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "Linear Regression"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in Artificial Intelligence"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "geography"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in Geography"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "AI"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in AI"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "AI"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in AI"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "AI"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in AI"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
      {
        "name": "file_url",
        "value": "https://en.wikipedia.org/wiki/Large_language_model"
      },
      {
        "name": "file_type",
        "value": "md"
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "ML"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in ML"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "CS"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in CS"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "AI"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in AI"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "AI"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in AI"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "Machine Learning"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in ML"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "ML"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in Machine Learning"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "Machine Learning"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in ML"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "ML"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in Machine Learning"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "Machine Learning"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in ML"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
      {
        "name": "file_url",
        "value": "https://drive.google.com/file/d/1JIZxgX4aLUUl5bHy5SE8OK7Eg9tT1ZkA/view"
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
  "type": "chat",
  "tool_data": {
    "tool_id": 6,
    "inputs": [
      {
        "name": "grade_level",
        "value": "college"
      },
      {
        "name": "course",
        "value": "Computer Science"
      },
      {
        "name": "instructor_name",
        "value": "Amrutha Vinayakam"
      },
      {
        "name": "instructor_title",
        "value": "Master in CS"
      },
      {
        "name": "unit_time",
        "value": "week"
      },
      {
        "name": "unit_time_value",
        "value": 8
      },
      {
        "name": "start_date",
        "value": "July, 4th, 2024"
      },
      {
        "name": "assessment_methods",
        "value": "project and exams"
      },
      {
        "name": "grading_scale",
        "value": "In percentages (100%)"
      },
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