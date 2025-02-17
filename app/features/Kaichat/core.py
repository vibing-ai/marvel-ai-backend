from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from app.services.schemas import ChatMessage, Message
import os

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

def build_prompt():
    """
    Build the prompt for the model.
    """
    
    template = read_text_file("prompt/kaichat-prompt.txt")
    prompt = PromptTemplate(
        template=template,
        input_variables=["text"],
    )
    
    return prompt


def executor(user_name: str, user_query: str, messages: list[Message], k=10):
    
    # create a memory list of last k = 3 messages
    chat_context = [
        ChatMessage(
            role=message.role, 
            type=message.type, 
            text=message.payload.text
        ) for message in messages[-k:]
    ]

    prompt = build_prompt()
    
    llm = GoogleGenerativeAI(model="gemini-1.0-pro") 
    
    chain =  prompt | llm
    
    response = chain.invoke({"chat_history": chat_context, "user_name": user_name, "user_query": user_query})
    
    return response
