import pytest

from app.assistants.curriculum_support.curriculum_coach.core import executor
from app.services.assistant_registry import Message, MessagePayload, MessageType, Role, UserInfo

base_attributes = {
    "user_info": UserInfo(
        user_name="Aaron",
        user_age=30,
        user_preference="Senior AI Engineer"
    )
}

def test_executor_translate_valid():
    result = executor(
        **base_attributes,
        messages = [
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Help me outline a new high school computer science course with an introduction to AI."
                )
            ),
            Message(
                role=Role.ai,
                type=MessageType.text,
                timestamp=None,
                payload=MessagePayload(
                    text="Okay, I can help you outline a new high school computer science course with an introduction to AI. Given your background as a Senior AI Engineer, Aaron, I'll tailor this to be both engaging for high schoolers and accurate in its AI fundamentals.\n\nHere’s a potential course outline:\n\n**Course Title:** Foundations of Computer Science with AI\n\n**Target Audience:** High School Students (Grades 9-12)\n\n**Course Objectives:**\n\n*   Understand fundamental computer science principles.\n*   Gain a foundational understanding of AI concepts and applications.\n*   Develop problem-solving and computational thinking skills.\n*   Encourage ethical considerations related to AI.\n\n**Course Outline:**\n\n**Module 1: Introduction to Computer Science** (4 weeks)\n\n*   Week 1: What is Computer Science?\n    *   Introduction to algorithms and computational thinking.\n    *   History of computing and its impact on society.\n*   Week 2: Programming Basics\n    *   Introduction to Python (or another suitable language).\n    *   Variables, data types, and basic input/output.\n*   Week 3: Control Structures\n    *   Conditional statements (if/else).\n    *   Loops (for, while).\n*   Week 4: Data Structures\n    *   Lists and arrays.\n    *   Basic operations (searching, sorting).\n\n**Module 2: Introduction to Artificial Intelligence** (6 weeks)\n\n*   Week 5: What is AI?\n    *   Defining AI and its various subfields (machine learning, NLP, computer vision).\n    *   Examples of AI in everyday life.\n*   Week 6: Machine Learning Basics\n    *   Introduction to machine learning concepts (supervised, unsupervised, reinforcement learning).\n    *   Simple linear regression example.\n*   Week 7: Supervised Learning\n    *   Classification algorithms (e.g., decision trees, k-nearest neighbors).\n    *   Training and testing data.\n*   Week 8: Unsupervised Learning\n    *   Clustering algorithms (e.g., k-means).\n    *   Dimensionality reduction.\n*   Week 9: Neural Networks\n    *   Introduction to neural networks and deep learning.\n    *   Basic architecture of a neural network.\n*   Week 10: AI Ethics and Societal Impact\n    *   Ethical considerations in AI (bias, fairness, privacy).\n    *   The impact of AI on jobs and society.\n\n**Module 3: AI Applications and Projects** (6 weeks)\n\n*   Week 11-12: Natural Language Processing (NLP)\n    *   Basics of NLP (tokenization, stemming).\n    *   Sentiment analysis project.\n*   Week 13-14: Computer Vision\n    *   Basics of computer vision (image classification).\n    *   Simple image recognition project.\n*   Week 15-16: AI Project Development\n    *   Students work on individual or group AI projects.\n    *   Project presentations and peer review.\n\n**Example Projects:**\n\n*   Sentiment analysis of social media posts.\n*   Simple image classifier.\n*   Chatbot using NLP.\n\nHow does that sound, Aaron?\n"
                )
            ),
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Please, summarize what you said and translate that to Spanish"
                )
            )
        ]
    )
    assert isinstance(result, str)

def test_executor_translate_invalid():
    with pytest.raises(TypeError) as exc_info:
        executor(
            messages=[
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                    "text":"Help me outline a new high school computer science course with an introduction to AI."
                    }
                },
                {
                    "role":"ai",
                    "type":"text",
                    "timestamp":None,
                    "payload":{
                    "text":"Okay, I can help you outline a new high school computer science course with an introduction to AI. Given your background as a Senior AI Engineer, Aaron, I'll tailor this to be both engaging for high schoolers and accurate in its AI fundamentals.\n\nHere’s a potential course outline:\n\n**Course Title:** Foundations of Computer Science with AI\n\n**Target Audience:** High School Students (Grades 9-12)\n\n**Course Objectives:**\n\n*   Understand fundamental computer science principles.\n*   Gain a foundational understanding of AI concepts and applications.\n*   Develop problem-solving and computational thinking skills.\n*   Encourage ethical considerations related to AI.\n\n**Course Outline:**\n\n**Module 1: Introduction to Computer Science** (4 weeks)\n\n*   Week 1: What is Computer Science?\n    *   Introduction to algorithms and computational thinking.\n    *   History of computing and its impact on society.\n*   Week 2: Programming Basics\n    *   Introduction to Python (or another suitable language).\n    *   Variables, data types, and basic input/output.\n*   Week 3: Control Structures\n    *   Conditional statements (if/else).\n    *   Loops (for, while).\n*   Week 4: Data Structures\n    *   Lists and arrays.\n    *   Basic operations (searching, sorting).\n\n**Module 2: Introduction to Artificial Intelligence** (6 weeks)\n\n*   Week 5: What is AI?\n    *   Defining AI and its various subfields (machine learning, NLP, computer vision).\n    *   Examples of AI in everyday life.\n*   Week 6: Machine Learning Basics\n    *   Introduction to machine learning concepts (supervised, unsupervised, reinforcement learning).\n    *   Simple linear regression example.\n*   Week 7: Supervised Learning\n    *   Classification algorithms (e.g., decision trees, k-nearest neighbors).\n    *   Training and testing data.\n*   Week 8: Unsupervised Learning\n    *   Clustering algorithms (e.g., k-means).\n    *   Dimensionality reduction.\n*   Week 9: Neural Networks\n    *   Introduction to neural networks and deep learning.\n    *   Basic architecture of a neural network.\n*   Week 10: AI Ethics and Societal Impact\n    *   Ethical considerations in AI (bias, fairness, privacy).\n    *   The impact of AI on jobs and society.\n\n**Module 3: AI Applications and Projects** (6 weeks)\n\n*   Week 11-12: Natural Language Processing (NLP)\n    *   Basics of NLP (tokenization, stemming).\n    *   Sentiment analysis project.\n*   Week 13-14: Computer Vision\n    *   Basics of computer vision (image classification).\n    *   Simple image recognition project.\n*   Week 15-16: AI Project Development\n    *   Students work on individual or group AI projects.\n    *   Project presentations and peer review.\n\n**Example Projects:**\n\n*   Sentiment analysis of social media posts.\n*   Simple image classifier.\n*   Chatbot using NLP.\n\nHow does that sound, Aaron?\n"
                    }
                },
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                    "text":"Please, summarize what you said and translate that to spanish"
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, TypeError)