import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
from app.services.assistant_registry import UserInfo
from app.services.logger import setup_logger
from app.tools.utils.tool_utilities import read_text_file

load_dotenv(find_dotenv())

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

logger = setup_logger()

model = genai.GenerativeModel(model_name='gemini-2.0-flash-exp',
                              system_instruction=read_text_file('prompt/co_teacher_context.txt'),
                              )

def run_co_teacher_assistant(user_query: str, chat_context: str, user_info: UserInfo):
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