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
    with pytest.raises(Exception):
        executor(
            **base_attributes,
            message=[
                Message(
                    role=Role.human,
                    type=MessageType.text,
                    timestamp="string",
                    payload=MessagePayload(
                        text="Give me insights on how to approach project-based learning activities"
                    )
                ),
                Message(
                    role=Role.ai,
                    type=MessageType.text,
                    timestamp=None,
                    payload=MessagePayload(
                        text=(
                            "Project-based learning (PBL) is an educational approach that involves students actively exploring real-world problems and challenges over an extended period. Here are some insights on how to effectively approach PBL activities:\n"
                            "\n"
                            "1. Define Clear Objectives: Start by identifying the learning goals and outcomes you want to achieve through the project. Ensure that these objectives align with curriculum standards and student interests.\n"
                            "\n"
                            "2. Choose Relevant Projects: Select projects that are meaningful and relevant to students' lives. Real-world applications increase engagement and motivation.\n"
                            "\n"
                            "3. Plan the Project Scope: Outline the project's scope, including timelines, resources needed, and key milestones. Break down the project into manageable phases.\n"
                            "\n"
                            "4. Foster Collaboration: Encourage teamwork and collaboration among students. Assign roles and responsibilities to promote accountability and diverse skill development.\n"
                            "\n"
                            "5. Integrate Research and Inquiry: Guide students to conduct research, ask questions, and seek out information independently. This promotes critical thinking and problem-solving skills.\n"
                            "\n"
                            "6. Provide Support and Resources: Be available to support students throughout the project. Provide access to necessary resources, tools, and materials.\n"
                            "\n"
                            "7. Encourage Reflection: Incorporate regular reflection sessions where students can discuss their progress, challenges faced, and lessons learned. This helps deepen understanding and self-assessment.\n"
                            "\n"
                            "8. Assess Holistically: Use a variety of assessment methods, including formative assessments, peer evaluations, and final presentations. Focus on both the process and the final product.\n"
                        )
                    )
                ),
                Message(
                    role=Role.human,
                    type=MessageType.text,
                    timestamp="string",
                    payload=MessagePayload(
                        text="What are some potential challenges in implementing project-based learning?"
                    )
                ),
                Message(
                    role=Role.ai,
                    type=MessageType.text,
                    timestamp=None,
                    payload=MessagePayload(
                        text=(
                            "Implementing project-based learning (PBL) can be highly effective, but it also comes with several potential challenges. Here are some common ones:\n"
                            "\n"
                            "1. Time Management: PBL often requires more time than traditional teaching methods. Balancing project work with other curriculum requirements can be challenging for both teachers and students.\n"
                            "\n"
                            "2. Resource Availability: Successful PBL may require access to various resources, including technology, materials, and community connections. Limited resources can hinder the effectiveness of projects.\n"
                            "3. Assessment Challenges: Evaluating student performance in PBL can be complex. Traditional assessment methods may not fully capture the skills and knowledge students gain through project work. \n"
                            "Developing appropriate rubrics and assessment criteria is essential but can be time-consuming.\n"
                            "\n"
                            "4. Student Readiness: Not all students may be prepared for the self-directed nature of PBL. Some may struggle with time management, collaboration, or independent research skills, requiring additional support and scaffolding from educators.\n"
                            "\n"
                        )
                    )
                )
            ]
        )
       