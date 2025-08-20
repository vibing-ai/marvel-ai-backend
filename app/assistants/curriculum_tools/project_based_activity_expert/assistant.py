import os
from dotenv import load_dotenv, find_dotenv
from app.services.assistant_registry import UserInfo
import google.generativeai as genai
from app.services.logger import setup_logger


logger = setup_logger()

load_dotenv(find_dotenv())
#genai.configure(api_key= os.environ("GOOGLE_API_KEY"))
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def read_text_file(filepath: str):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, filepath)
    
    # Read and return the file content
    with open(absolute_file_path, 'r') as file:
        return file.read()
    
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    system_instruction=read_text_file('prompt/project_based_activity_prompt.txt'),
    )
    
def run_project_based_activity(user_info: UserInfo, user_query: str, chat_context: str):
    chat = model.start_chat()
    user_name = user_info.user_name
    user_age = user_info.user_age
    user_preference = user_info.user_preference

    response = chat.send_message(f"""
                                 User query: {user_query}\n
                                 Personalize the response for {user_name} (Age: {user_age}) with preference: {user_preference}.\n
                                 You can use the chat context if further information is needed: {chat_context}\n
                                 """)
    return response.text
    

    

   

      
        
        
        

    