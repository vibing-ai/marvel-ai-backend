import pytest

from app.assistants.curriculum_tools.project_based_activity_expert.core import executor
from app.services.assistant_registry import UserInfo, Message, Role, MessageType, MessagePayload


base_attributes = {
    "user_info": UserInfo(
        user_name="Makafui",
        user_age=25,
        user_preference = "Senior Software Engineer"
    )
}

def test_executor_translate_valid():
    # First create a testing parameter for the human input 
    # Second create a testing parameter for the Ai response
    result = executor(
        **base_attributes,
        message=[
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Suggest a project-based activity for an aspiring software engineer looking to sharpen skills in backend development"
                )
            ),
            Message(
                role=Role.ai,
                type=MessageType.text,
                timestamp=None,
                payload=MessagePayload(
                    text=(
                        "This project is designed for an aspiring software engineer focusing on backend development skills. \n"
                        "It emphasizes core concepts like API design, database integration, authentication, and error handling, while being scalable for individual work. "
                        "Assuming a beginner-to-intermediate level (familiarity with a programming language but needing practice in backend frameworks), this can be completed in 1-2 weeks part-time, using free tools like a local development environment (e.g., VS Code, Git). If you have a preferred backend language or framework (e.g., Node.js, Python, Java), let me know for more tailored adjustments."
                        "*Rationale\n"
                        "This project aligns with backend development goals by simulating real-world server-side tasks: handling data persistence, user sessions, and API endpoints.\n"
                        "It promotes critical thinking through decisions on data models and security, while encouraging collaboration if extended to a group (e.g., one person handles auth, another database).\n"
                        "It's hands-on and results in a portfolio-worthy demo, applicable to job interviews or personal use."
                        "*Project Description\n"
                        "Create a backend API for a task management application (like a simplified Todoist). Users can register, log in, create/update/delete tasks, and categorize them (e.g., by priority). The API will use a database for storage and include basic authentication to secure endpoints."
                        "*Key Learning Objectives\n"
                        "Design and implement RESTful endpoints.\n"
                        "Integrate a database for CRUD operations.\n"
                        "Handle user authentication and authorization.\n"
                        "Implement error handling and validation.\n"
                        "*Required Resources\n"
                        "Programming language/framework: Node.js with Express (JavaScript), or Python with FastAPI/Flask.\n"
                        "Database: MongoDB (NoSQL, free cloud tier via MongoDB Atlas) or PostgreSQL (SQL, free local install via Docker).\n"
                        "Tools: Postman or Insomnia for API testing; Git for version control.\n"
                        "Time: 10-20 hours.\n"
                        
                        "*Actionable Steps\n"
                        "Setup Environment: Install necessary packages (e.g., via npm for Node.js: express, mongoose, bcrypt, jsonwebtoken). Set up a project repository on GitHub.\n"
                        "Design Data Models: Define schemas for users (email, password hash) and tasks (title, description, due date, status, user ID).\n"
                        "Implement Authentication: Create endpoints for user registration (/register) and login (/login). Use JWT for tokens and hashing for passwords.\n"
                        "Build Core Endpoints: Develop CRUD routes for tasks (/tasks: GET all, POST new; /tasks/:id: GET one, PUT update, DELETE remove). Ensure only authenticated users access their tasks.\n"
                        "Add Features: Implement filtering (e.g., by status) and validation (e.g., required fields).\n"
                        "Test and Deploy: Write unit tests for endpoints. Optionally deploy to a free host like Render or Vercel.\n"
                        "Document: Create a README with API docs (using Swagger or manual endpoints list).\n"
                        
                        "*Deliverables\n"
                        "A working API server (run locally or deployed).\n"
                        "Source code repository.\n"
                        "API documentation with example requests/responses.\n"
                        "Self-reflection: A short write-up on challenges faced (e.g., debugging auth) and skills gained.\n"
                        
                        "*Assessment Criteria (for Self-Evaluation)\n"
                        "Functionality: All endpoints work as expected (test with 5-10 scenarios).\n"
                        "Code Quality: Clean, modular code with comments; proper error handling.\n"
                        "Security: No plain-text passwords; protected routes.\n"
                        "Scalability: Database queries are efficient (e.g., indexed fields).\n"

                        "*Customization Options\n"
                        "For Beginners: Start with in-memory storage instead of a database to focus on API basics, then add persistence later.\n"
                        "For Advanced Learners: Integrate email notifications (using Nodemailer) or real-time updates (WebSockets with Socket.io). Add role-based access if simulating a team app.\n"
                        "Language Variations: Switch to Java Spring Boot for enterprise-style backend, or Go with Gin for performance-focused learning.\n"
                        "Interdisciplinary Twist: Connect to a frontend (e.g., React app) for full-stack practice, or incorporate AI (e.g., integrate OpenAI API for task suggestions).\n"
                        "Group Adaptation: In a small group (2-3 people), divide tasks: one on database, one on auth, one on testing.\n"
                        "Resource Constraints: If no cloud database, use SQLite for local SQL practice.\n"
                    )
                )            
            ),
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Provide a concise summary of the project-based activity suitable for a quick overview."
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
                    "text":"Give me insights for personalized teaching"
                    }
                },
                {
                    "role":"ai",
                    "type":"text",
                    "timestamp":None,
                    "payload":{
                    "text":"Okay, Aaron, as a Senior AI Engineer, you're likely someone who values data-driven strategies and innovative solutions. Let's tailor some insights for personalized teaching with that in mind. Here's how you can approach this, leveraging your analytical and problem-solving skills:\n\n**1. Data-Driven Student Understanding:**\n\n*   **Analytics Approach:** Just like in AI projects, you can analyze student performance data to identify patterns and tailor your teaching methods. Look at areas where students excel and where they struggle. Use this data to understand the varying needs of your students.\n*   **Actionable Steps:**\n    *   Use formative assessments (quizzes, exit tickets, in-class activities) to collect data.\n    *   Create a spreadsheet or use a digital tool to track student performance across different topics or skills.\n    *   Identify individual student strengths, areas of improvement, and preferred learning styles.\n\n**2. Adaptive Content and Delivery:**\n\n*   **Modular Content Creation:** Think of your teaching material like modular code, where you can easily modify and adapt it. Develop a core set of learning materials and then adapt to student needs by offering multiple versions (different problem sets, examples, or explanations).\n*   **Actionable Steps:**\n    *   Develop a resource repository of varying complexity levels for each topic.\n    *   Experiment with different media formats (videos, interactive simulations, audio explanations) to cater to diverse learning preferences.\n    *   Offer a range of choices in how students approach their learning - which project they want to work on, which practice questions they attempt, etc.\n\n**3. Algorithm-Based Feedback:**\n\n*   **Timely and Specific Feedback:** Aim to provide feedback that is not only timely but also very specific. Think of it as debugging a code – the feedback needs to pinpoint the problem precisely.\n*   **Actionable Steps:**\n    *   Use rubrics for grading that clearly outline expectations.\n    *   Provide feedback that is focused on the concepts, not just the final answer.\n    *   Use automated tools, where possible, to offer initial feedback, allowing you to focus on more complex issues.\n\n**4. Collaborative Problem-Solving:**\n\n*   **Agile Team Teaching:** Approach your classroom as an agile team working on a project. Encourage collaboration and peer-to-peer learning.\n*   **Actionable Steps:**\n    *   Implement group activities with defined roles, as you might in a project team.\n    *   Have students teach each other concepts, thereby reinforcing their own understanding.\n    *   Use pair programming or group programming tasks to foster learning from each other.\n\n**5. Iterative Teaching Process:**\n\n*   **Continuous Improvement:** Just like in software development, use a continuous improvement approach to your teaching. Regularly evaluate your teaching practices and make adjustments based on results.\n*   **Actionable Steps:**\n    *   Solicit student feedback on your teaching methods and the content.\n    *   Periodically reflect on what works and what doesn't.\n    *   Don't be afraid to experiment with new approaches based on feedback and data.\n\nAaron, your experience with AI and data analysis can be a powerful asset in personalizing your teaching approach. By treating your classroom as a dynamic system with evolving needs, you can create a learning environment that is truly tailored to each of your students. You have an analytical mindset and the tools to make data driven decisions in the classroom. By embracing these strategies, you'll be able to provide a more engaging and effective learning experience for your students! Let me know if you want to explore any of these strategies further.\n"
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