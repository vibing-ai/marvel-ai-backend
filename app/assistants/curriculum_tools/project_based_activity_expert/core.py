
from app.services.schemas import (
    ChatMessage
)
from app.assistants.curriculum_tools.project_based_activity_expert.assistant import run_project_based_activity
from app.services.logger import setup_logger
from app.services.assistant_registry import UserInfo, Message
logger = setup_logger()

def executor(user_info: UserInfo, messages: list[Message]=None, k: int = 3):
   logger.info("Generating Project Based Activity")
   
   chat_context_list = [ 
       ChatMessage(
           role = message.role,
           type = message.type,
           text = message.payload.text
       ) for message in messages[-k:]
   ]
   
   chat_context_string = "\n\n".join(
       map(
           lambda message: (
               f"Role: {message.role}\n"
               f"Type: {message.type}\n"
               f"Text: {message.text}\n"
           ),
           chat_context_list
       )
   )

   response = run_project_based_activity(
       user_info=user_info,
       user_query=chat_context_list[-1].text,
       chat_context=chat_context_string
   )
   logger.info(f"Response generated successfully for Project Based Activity: {response}")
   return response


   
    
   
   