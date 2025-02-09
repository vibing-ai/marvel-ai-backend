from app.assistants.curriculum_support.curriculum_coach.assistant import run_curriculum_coach
from app.services.assistant_registry import Message, UserInfo
from app.services.logger import setup_logger
from app.services.schemas import (
    ChatMessage
)

logger = setup_logger()

def executor(
        user_info: UserInfo,
        messages: list[Message]=None, 
        k=3
    ):
    
    logger.info(f"Generating response from Curriculum coach")

    chat_context_list = [
        ChatMessage(
            role=message.role, 
            type=message.type, 
            text=message.payload.text
        ) for message in messages[-k:]
    ]

    chat_context_string = "\n\n".join(
        map(
            lambda message: (
                f"Role: {message.role}\n"
                f"Type: {message.type}\n"
                f"Text: {message.text}"
            ),
            chat_context_list        
        )
    )
    
    response = run_curriculum_coach(
        user_query=chat_context_list[-1].text,
        chat_context=chat_context_string,
        user_info=user_info
    )

    logger.info(f"Response generated successfully for Curriculum coach: {response}")

    return response