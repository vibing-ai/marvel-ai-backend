from enum import Enum

class FileType(Enum):
    PDF = 'pdf'
    CSV = 'csv'
    TXT = 'txt'
    MD = 'md'
    URL = "url"
    PPTX = 'pptx'
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"
    XML = 'xml'

    GDOC = 'gdoc'
    GSHEET = "gsheet"
    GSLIDE = "gslide"
    GPDF = 'gpdf'

    YOUTUBE_URL = 'youtube_url' 