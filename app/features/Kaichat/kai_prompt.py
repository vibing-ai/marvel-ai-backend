from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    ChatPromptTemplate,
)

def generate_kai_prompt(firstname, user_query, history):
    """
    Generates a dynamic and interactive prompt for KAI, incorporating user history and query.
    """
    greeting = f"Hello {firstname}! I'm here to help with your teaching and educational strategies."
    if not user_query:
        request_info = "Could you please tell me more about what you need help with today?"
    else:
        request_info = f"Based on your question about '{user_query}', here's what I suggest:"

    error_handling = "If you have questions outside of educational topics, please let me know, and I'll guide you to the appropriate resources."

    history_feedback = "Looking at our last conversation, you were interested in behavior management strategies. Do you need more information on that?"
    
    additional_help = "What other topics in education would you like to explore today?"

    prompt = f"""
{greeting}
{request_info}
{history_feedback}
{error_handling}
{additional_help}
    """
    return prompt

def join_prompt(firstname, user_query, history):
    """
    Creates a full chat template that incorporates system and human messages, enhancing the interaction.
    """
    system_prompt = generate_kai_prompt(firstname, user_query, history)
    system_msg_template = SystemMessagePromptTemplate.from_template(system_prompt)

    human_prompt = "Please type your response or question below:"
    human_msg_template = HumanMessagePromptTemplate.from_template(human_prompt)

    chat_template = ChatPromptTemplate.from_messages(
        [
            system_msg_template,
            MessagesPlaceholder(variable_name="history"),
            human_msg_template,
        ]
    )

    return chat_template
