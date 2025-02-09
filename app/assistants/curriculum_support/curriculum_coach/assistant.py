import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
from app.services.assistant_registry import UserInfo
from app.services.logger import setup_logger

load_dotenv(find_dotenv())

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

logger = setup_logger()

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

model = genai.GenerativeModel(model_name='gemini-2.0-flash-exp',
                              system_instruction=read_text_file('prompt/curriculum_coach_context.txt'),
                              )

def run_curriculum_coach(user_query: str, chat_context: str, user_info: UserInfo):
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