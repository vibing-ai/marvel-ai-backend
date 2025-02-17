from langchain_community.document_loaders import YoutubeLoader, PyPDFLoader, TextLoader, UnstructuredURLLoader, UnstructuredPowerPointLoader, Docx2txtLoader, UnstructuredExcelLoader, UnstructuredXMLLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.allowed_file_extensions import FileType
from app.api.error_utilities import FileHandlerError, ImageHandlerError
from app.api.error_utilities import VideoTranscriptError
from langchain_core.messages import HumanMessage
from app.services.logger import setup_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pydub import AudioSegment
from google.cloud import speech
from google.cloud.speech import RecognitionAudio, RecognitionConfig
from google.cloud import speech_v1p1beta1 as speech
from dotenv import load_dotenv, find_dotenv
import speech_recognition as sr
import tempfile
import uuid
import requests
import gdown
import shutil
import io
import os
import base64

load_dotenv(find_dotenv())

STRUCTURED_TABULAR_FILE_EXTENSIONS = {"csv", "xls", "xlsx", "gsheet", "xml"}
FILE_TYPES_TO_CHECK = {'pdf', 'csv', 'txt', 'pptx'}


logger = setup_logger(__name__)

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 100
)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()

def get_docs(file_url: str, file_type: str, lang: str = "en", verbose=True):
    file_type = file_type.lower()

    if file_type in FILE_TYPES_TO_CHECK:
        try:
            # Make a HEAD request to get content type
            head_response = requests.head(file_url, allow_redirects=True)
            content_type = head_response.headers.get('Content-Type') 
            if content_type is None:
                raise FileHandlerError(f"Failed to retrieve Content-Type from URL ", file_url)
            # If the content type is HTML
            if 'text/html' in content_type:
                file_type = "url"
                logger.info("text/html in content_type: change file_type to url")  
        
        except requests.exceptions.RequestException as e:
            exception_map = {
                requests.exceptions.MissingSchema: "Invalid URL format.",
                requests.exceptions.ConnectionError: "Failed to connect to the server.",
                requests.exceptions.Timeout: "Request timed out.",
            }
            # Check if the exception is in the map; if not, default to a generic message
            error_message = exception_map.get(type(e), f"Request failed: {e}")
            logger.error(error_message)
            raise FileHandlerError(error_message, file_url)
  
    try:
        file_loader = file_loader_map[FileType(file_type)]
        if "generate_docs_from_audio_gcloud" in file_loader.__name__:
            docs = file_loader(file_url, lang, verbose)
        else:
            docs = file_loader(file_url, verbose)
        return docs

    except KeyError:
        logger.error(f"Unsupported file type: {file_type}")
        raise FileHandlerError(f"Unsupported file type", file_url)
    
    except Exception as e:
        logger.error(f"Failed to load the document: {e}")
        raise FileHandlerError(f"Document loading failed", file_url)

def load_url_documents(url: str, verbose=False):
    try:
        # Using the global session to load documents with custom headers
        url_loader = UnstructuredURLLoader(urls=[url])
        docs = url_loader.load()
            
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error occurred: {e}")
        raise FileHandlerError(f"Failed to load document from URL due to HTTP error", url) from e
    except Exception as e:
        logger.error(f"Failed to load document from URL: {e}")
        raise FileHandlerError(f"Failed to load document from URL", url)
    
    if docs:
        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found URL")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs




class FileHandler:
    def __init__(self, file_loader, file_extension):
        self.file_loader = file_loader
        self.file_extension = file_extension

    def load(self, url):
        # Generate a unique filename with a UUID prefix
        unique_filename = f"{uuid.uuid4()}.{self.file_extension}"

        try:
            # Download the file from the URL and save it to a temporary file
            response = requests.get(url, timeout=10)  
            response.raise_for_status()  # Raise an HTTPError for bad responses

            with tempfile.NamedTemporaryFile(delete=False, prefix=unique_filename) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name

        except requests.exceptions.RequestException as req_err:
            logger.error(f"HTTP request error: {req_err}")
            raise FileHandlerError(f"Failed to download file from URL", url) from req_err
        except Exception as e:
            logger.error(f"An error occurred while downloading or saving the file: {e}")
            raise FileHandlerError(f"Failed to handle file download", url) from e

        # Use the file_loader to load the documents
        try:
            loader = self.file_loader(file_path=temp_file_path)
        except Exception as e:
            logger.error(f"No such file found at {temp_file_path}")
            raise FileHandlerError(f"No file found", temp_file_path) from e

        try:
            documents = loader.load()
        except Exception as e:
            logger.error(f"File content might be private or unavailable or the URL is incorrect.")
            raise FileHandlerError(f"No file content available", temp_file_path) from e

        # Remove the temporary file
        os.remove(temp_file_path)

        return documents

def load_pdf_documents(pdf_url: str, verbose=False):
    pdf_loader = FileHandler(PyPDFLoader, "pdf")
    docs = pdf_loader.load(pdf_url)

    if docs:
        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found PDF file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs


def load_csv_documents(csv_url: str, verbose=False):
    csv_loader = FileHandler(CSVLoader, "csv")
    docs = csv_loader.load(csv_url)

    if docs:
        if verbose:
            logger.info(f"Found CSV file")
            logger.info(f"Splitting documents into {len(docs)} chunks")

        return docs

def load_txt_documents(notes_url: str, verbose=False):
    notes_loader = FileHandler(TextLoader, "txt")
    docs = notes_loader.load(notes_url)

    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found TXT file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_md_documents(notes_url: str, verbose=False):
    notes_loader = FileHandler(TextLoader, "md")
    docs = notes_loader.load(notes_url)

    if docs:

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found MD file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_pptx_documents(pptx_url: str, verbose=False):
    pptx_handler = FileHandler(UnstructuredPowerPointLoader, 'pptx')

    docs = pptx_handler.load(pptx_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found PPTX file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_docx_documents(docx_url: str, verbose=False):
    docx_handler = FileHandler(Docx2txtLoader, 'docx')
    docs = docx_handler.load(docx_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found DOCX file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_xls_documents(xls_url: str, verbose=False):
    xls_handler = FileHandler(UnstructuredExcelLoader, 'xls')
    docs = xls_handler.load(xls_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found XLS file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_xlsx_documents(xlsx_url: str, verbose=False):
    xlsx_handler = FileHandler(UnstructuredExcelLoader, 'xlsx')
    docs = xlsx_handler.load(xlsx_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found XLSX file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_xml_documents(xml_url: str, verbose=False):
    xml_handler = FileHandler(UnstructuredXMLLoader, 'xml')
    docs = xml_handler.load(xml_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found XML file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs


class FileHandlerForGoogleDrive:
    def __init__(self, file_loader, file_extension='docx'):
        self.file_loader = file_loader
        self.file_extension = file_extension

    def load(self, url):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                unique_filename = os.path.join(temp_dir, f"{uuid.uuid4()}.{self.file_extension}")
                
                logger.info(f"Downloading file from URL: {url}")
                
                try:
                    gdown.download(url=url, output=unique_filename, fuzzy=True)
                    logger.info(f"File downloaded successfully to {unique_filename}")
                except Exception as e:
                    logger.error(e)
                    logger.error("File content might be private or unavailable, or the URL is incorrect.")
                    raise FileHandlerError("No file content available") from e

                try:
                    loader = self.file_loader(file_path=unique_filename)
                except Exception as e:
                    logger.error(f"No such file found at {unique_filename}")
                    raise FileHandlerError("No file found", unique_filename) from e

                try:
                    documents = loader.load()
                    logger.info("File loaded successfully.")
                except Exception as e:
                    logger.error(e)
                    logger.error("Error loading file content.")
                    raise FileHandlerError("No file content available") from e

                return documents
        except Exception as e:
            logger.error("An unexpected error occurred during the file handling process.")
            raise e
        
def load_gdocs_documents(drive_folder_url: str, verbose=False):

    gdocs_loader = FileHandlerForGoogleDrive(Docx2txtLoader)

    docs = gdocs_loader.load(drive_folder_url)

    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found Google Docs files")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_gsheets_documents(drive_folder_url: str, verbose=False):
    gsheets_loader = FileHandlerForGoogleDrive(UnstructuredExcelLoader, 'xlsx')
    docs = gsheets_loader.load(drive_folder_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found Google Sheets files")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_gslides_documents(drive_folder_url: str, verbose=False):
    gslides_loader = FileHandlerForGoogleDrive(UnstructuredPowerPointLoader, 'pptx')
    docs = gslides_loader.load(drive_folder_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found Google Slides files")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        return split_docs

def load_gpdf_documents(drive_folder_url: str, verbose=False):

    gpdf_loader = FileHandlerForGoogleDrive(PyPDFLoader,'pdf')

    docs = gpdf_loader.load(drive_folder_url)
    if docs: 

        if verbose:
            logger.info(f"Found Google PDF files")
            logger.info(f"Splitting documents into {len(docs)} chunks")

        return docs

def load_docs_youtube_url(youtube_url: str, verbose=True) -> str:
    try:
        loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=False)
    except Exception as e:
        logger.error(f"No such video found at {youtube_url}")
        raise VideoTranscriptError(f"No video found", youtube_url) from e

    try:
        docs = loader.load()
        
    except Exception as e:
        logger.error(f"Video transcript might be private or unavailable in 'en' or the URL is incorrect.")
        raise VideoTranscriptError(f"No video transcripts available", youtube_url) from e
    
    if verbose:
        logger.info(f"Found video")
        logger.info(f"Combined documents into a single string.")
        logger.info(f"Beginning to process transcript...")

    split_docs = splitter.split_documents(docs)

    return split_docs

llm_for_img = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def generate_docs_from_img(img_url, verbose: bool=False):
    message = HumanMessage(
    content=[
            {
                "type": "text",
                "text": "Give me a summary of what you see in the image. It must be 3 detailed paragraphs.",
            }, 
            {"type": "image_url", "image_url": img_url},
        ]
    )

    try:
        response = llm_for_img.invoke([message]).content
        logger.info(f"Generated summary: {response}")
        docs = Document(page_content=response, metadata={"source": img_url})
        split_docs = splitter.split_documents([docs])
    except Exception as e:
        logger.error(f"Error processing the request due to Invalid Content or Invalid Image URL")
        raise ImageHandlerError(f"Error processing the request", img_url) from e

    return split_docs

#########################################################################################################
#########################################################################################################

#USING GOOGLE WEB SPEECH API (FREE SERVICE USED FOR WEB TRANSCRIPT)
def generate_docs_from_audio(audio_url: str, verbose=False):
    
    logger.info("INSIDE generate_docs_from_audio")
    try:
        # Attempt to create a temporary directory
        temp_dir = tempfile.mkdtemp()
        if verbose:
            print(f"Temporary directory created: {temp_dir}")

    except OSError as e:
        # Handle any errors that occur while interacting with the file system
        logger.error(f"Failed to create temporary directory: {e}")
        raise Exception(f"An error occurred while creating the temporary directory: {e}")


    # Generate unique file names for the MP3 and WAV files
    mp3_audio = f'mp3_audio_{uuid.uuid4()}.mp3'
    wav_audio = f'wav_audio_{uuid.uuid4()}.wav'
    wav_file_path = os.path.join(temp_dir, wav_audio)
    
    docs = []

    # Download the file from the URL and save it to a temporary file
    try:
        response = requests.get(audio_url)
        response.raise_for_status()  # Ensure the request was successful
    except (requests.exceptions.RequestException) as req_err:
        logger.error(f"Error occurred while downloading audio: {req_err}")
        raise Exception(f"Error occurred while downloading audio: {req_err}")

    with tempfile.NamedTemporaryFile(delete=False, prefix=mp3_audio) as temp_file:
        temp_file.write(response.content)
        mp3_file_path = temp_file.name
        logger.info(f"mp3_file_path: {mp3_file_path}")

    # Convert the MP3 file to WAV
    try:
        audio = AudioSegment.from_mp3(mp3_file_path)
        audio.export(wav_file_path, format="wav")
        if verbose:
            print("Conversion to WAV successful!")
    except Exception as e:
        logger.error(f"Failed to convert MP3 to WAV: {e}")
        raise Exception(f"Failed to convert MP3 to WAV: {e}")


    # Split WAV file into smaller chunks
    chunk_length_ms = 60000  # 1-minute chunks
    chunks = split_audio_fixed_intervals(audio, chunk_length_ms)

    # Create a recognizer instance
    recognizer = sr.Recognizer()

    # Process each chunk
    for i, chunk in enumerate(chunks):
        chunk_file_path = os.path.join(temp_dir, f'chunk_{i}.wav')
        try:
            # Export the chunk to a file
            chunk.export(chunk_file_path, format="wav")
        except Exception as e:
            raise Exception(f"Failed to export chunk {i} to file: {e}")

        try:
            with sr.AudioFile(chunk_file_path) as source:
                audio_data = recognizer.record(source)
                logger.info(f"Audio data recorded for chunk {i} :{chunk_file_path}. Duration: {len(audio_data.frame_data) / audio_data.sample_rate:.2f} seconds")

                if len(audio_data.frame_data) == 0:
                    logger.warning(f"Warning: No audio data recorded for chunk {i}")
                    continue

                try:
                    # Recognize speech using Google web speech API
                    text = recognizer.recognize_google(audio_data)
                    docs.append(Document(page_content=text))  # Create Document objects from text
                    if verbose:
                        print(f"Transcription for chunk {i} successful: {text}")
                except sr.UnknownValueError:
                    logger.warning(f"Chunk {i}: Google Speech Recognition could not understand the audio.")
                except sr.RequestError as e:
                    logger.error(f"Chunk {i}: Could not request results from Google Speech Recognition service: {e}")
        except FileNotFoundError:
            logger.error(f"Chunk file not found: {chunk_file_path}")
        except Exception as e:
            logger.error(f"Unexpected error occurred while processing chunk {i}: {e}")
            raise Exception(f"Unexpected error during chunk processing: {e}")

    # Clean up temporary files
    try:    
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
            if verbose:
                print(f"Temporary WAV file {wav_file_path} deleted.")
        if os.path.exists(mp3_file_path):
            os.remove(mp3_file_path)
            if verbose:
                print(f"Temporary MP3 file {mp3_audio} deleted.")
        shutil.rmtree(temp_dir, ignore_errors=True)
        if verbose:
            print("Temporary directory deleted.")
    
    except OSError as e:
        logger.error(f"Error during cleanup temporary files: {e}")
        if verbose:
            print(f"Error during cleanup: {e}")

    if docs:
        split_docs = splitter.split_documents(docs)
        if verbose:
            logger.info("Found transcript")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")
        return split_docs

#########################################################################################################
#########################################################################################################
# Retrieve the API key from environment variables
# GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_API_KEY')
# if not GOOGLE_CLOUD_API_KEY:
#     raise ValueError("API key not found. Please check your .env file.")

# GOOGLE_CLOUD_SPEECH_TO_TEXT_URL = os.getenv('GOOGLE_SPEECH_URL')
# if not GOOGLE_CLOUD_SPEECH_TO_TEXT_URL:
#     raise ValueError("GOOGLE_CLOUD_SPEECH_TO_TEXT_URL not found. Please check your .env file.")

#USING GOOGLE SPEECH-TO-TEXT API (PAID SERVICE)(RECOMMENDED FOR LARGE AUDIO FILES)
def generate_docs_from_audio_gcloud(audio_url: str, lang: str, verbose=False):
#     logger.info("INSIDE generate_docs_from_audio_gcloud")
#     try:
#         # Attempt to create a temporary directory
#         temp_dir = tempfile.mkdtemp()
#         if verbose:
#             print(f"Temporary directory created: {temp_dir}")

#     except OSError as e:
#         # Handle any errors that occur while interacting with the file system
#         logger.error(f"Failed to create temporary directory: {e}")
#         raise Exception(f"An error occurred while creating the temporary directory: {e}")
    

#     # Generate unique file names for the MP3 and WAV files
#     mp3_audio = f'mp3_audio_{uuid.uuid4()}.mp3'
#     wav_audio = f'wav_audio_{uuid.uuid4()}.wav'
#     wav_file_path = os.path.join(temp_dir, wav_audio)

#     docs = []

#     # Download the file from the URL and save it to a temporary file
#     try:
#         response = requests.get(audio_url)
#         response.raise_for_status()  # Ensure the request was successful
#     except (requests.exceptions.RequestException) as req_err:
#         logger.error(f"Error occurred while downloading audio: {req_err}")
#         raise Exception(f"Error occurred while downloading audio: {req_err}")

#     with tempfile.NamedTemporaryFile(delete=False, prefix=mp3_audio) as temp_file:
#         temp_file.write(response.content)
#         mp3_file_path = temp_file.name
#         logger.info(f"mp3_file_path: {mp3_file_path}")

#     # Convert the MP3 file to WAV
#     audio = AudioSegment.from_mp3(mp3_file_path)
#     audio.export(wav_file_path, format="wav")
#     if verbose:
#         print("Conversion to WAV successful!")

#     # Split WAV file into smaller chunks with a slightly reduced length to avoid exceeding the limit
#     chunk_length_ms = 59000  # 59 seconds to ensure it's under the 1-minute limit for the API
#     chunks = split_audio_fixed_intervals(audio, chunk_length_ms)


#     # Google Cloud Speech-to-Text API URL
#     url = GOOGLE_CLOUD_SPEECH_TO_TEXT_URL

#     # Process each chunk
#     for i, chunk in enumerate(chunks): 
#         chunk_file_path = os.path.join(temp_dir, f'chunk_{i}.wav')
#         try:
#             # Export the chunk to a file
#             chunk.export(chunk_file_path, format="wav")
#         except Exception as e:
#             raise Exception(f"Failed to export chunk {i} to file: {e}")
        
#         try:
#             # Load the audio data and encode it in base64
#             with open(chunk_file_path, "rb") as audio_file:
#                 content = base64.b64encode(audio_file.read()).decode('utf-8')

#             headers = {
#                 'Content-Type': 'application/json',
#             }

#             params = {
#                 'key': GOOGLE_CLOUD_API_KEY,
#             }

#             data = {
#                 "config": {
#                     "encoding": "LINEAR16",
                    
#                     "languageCode": lang,
#                 },
#                 "audio": {
#                     "content": content
#                 }
#             }

#             # Send the request to the Speech-to-Text API
#             try:
#                 response = requests.post(url, headers=headers, params=params, json=data)
#                 response.raise_for_status()
#             except requests.exceptions.RequestException as e:
#                 logger.error(f"API request failed for chunk {i}: {e}")
#                 logger.error(f"Response content: {response.content}")
#                 continue

#             # Process the response
#             result = response.json()
#             for result in result.get('results', []):
#                 text = result['alternatives'][0]['transcript']
#                 docs.append(Document(page_content=text))
#             if verbose:
#                 print(f"Transcription for chunk {i} successful: {text}")

#         except FileNotFoundError:
#             logger.error(f"Chunk file not found: {chunk_file_path}")
#         except Exception as e:
#             logger.error(f"Unexpected error occurred while processing chunk {i}: {e}")
#             raise Exception(f"Unexpected error during chunk processing: {e}")


#    # Clean up temporary files
#     try:    
#         if os.path.exists(wav_file_path):
#             os.remove(wav_file_path)
#             if verbose:
#                 print(f"Temporary WAV file {wav_file_path} deleted.")
#         if os.path.exists(mp3_file_path):
#             os.remove(mp3_file_path)
#             if verbose:
#                 print(f"Temporary MP3 file {mp3_audio} deleted.")
#         shutil.rmtree(temp_dir, ignore_errors=True)
#         if verbose:
#             print("Temporary directory deleted.")
    
#     except OSError as e:
#         logger.error(f"Error during cleanup temporary files: {e}")
#         if verbose:
#             print(f"Error during cleanup: {e}")

#     if docs:
#         split_docs = splitter.split_documents(docs)
#         if verbose:
#             logger.info("Found transcript")
#             logger.info(f"Splitting documents into {len(split_docs)} chunks")
#         return split_docs
    return "Mocked Function"


def split_audio_fixed_intervals(audio: AudioSegment, interval_ms: int):
    """
    Split audio into chunks of fixed length.

    Args:
        audio (AudioSegment): The audio segment to split.
        interval_ms (int): The length of each chunk in milliseconds.

    Returns:
        List[AudioSegment]: List of audio chunks.
    """
    chunks = []
    length_ms = len(audio)

    # Split the audio into chunks
    for start in range(0, length_ms, interval_ms):
        end = min(start + interval_ms, length_ms)
        chunk = audio[start:end]
        chunks.append(chunk)

    # Verify the length of each chunk
    for i, chunk in enumerate(chunks):
        logger.info(f"Chunk {i} length: {len(chunk)} ms")

    return chunks

#########################################################################################################
#########################################################################################################


file_loader_map = {
    FileType.PDF: load_pdf_documents,
    FileType.CSV: load_csv_documents,
    FileType.TXT: load_txt_documents,
    FileType.MD: load_md_documents,
    FileType.URL: load_url_documents,
    FileType.PPTX: load_pptx_documents,
    FileType.DOCX: load_docx_documents,
    FileType.XLS: load_xls_documents,
    FileType.XLSX: load_xlsx_documents,
    FileType.XML: load_xml_documents,
    FileType.GDOC: load_gdocs_documents,
    FileType.GSHEET: load_gsheets_documents,
    FileType.GSLIDE: load_gslides_documents,
    FileType.GPDF: load_gpdf_documents,
    FileType.YOUTUBE_URL: load_docs_youtube_url,
    FileType.IMG: generate_docs_from_img,
    FileType.MP3: generate_docs_from_audio,
    FileType.GMP3: generate_docs_from_audio_gcloud
}