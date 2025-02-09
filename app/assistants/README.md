# Assistants Framework Overview

This repository hosts the implementation of a modular architecture for a variety of educational assistants designed to enhance teaching and learning experiences. The assistants are categorized into three main groups:


| **Curriculum Tools** | **Classroom Support** | **Communication & Tech Integration** |
| ---------------------- | ----------------------- | -------------------------------------- |
| Coming Soon          | **CoTeacher**         | Coming Soon                          |

## Implemented Assistants

### CoTeacher

CoTeacher, part of the **Classroom Support** category, is an advanced AI assistant designed to aid educators by offering multilingual support and personalized interactions. With its ability to adapt to user preferences, CoTeacher ensures inclusivity by seamlessly accommodating diverse languages and teaching styles, making it an invaluable tool for fostering effective and engaging learning experiences.

## Features and Payloads

Below are the JSON payloads for the implemented actions of CoTeacher.

### CoTeacher

**Request:**

```json
{
   "assistant_inputs":{
      "assistant_group":"classroom_support",
      "assistant_name":"co_teacher",
      "user_info":{
         "user_name":"Aaron Sosa",
         "user_age":26,
         "user_preference":"Senior AI Engineer"
      },
      "messages":[
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
            "timestamp":null,
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
   }
}
```

**Response:**

```json
{
  "data": [
    {
      "role": "ai",
      "type": "text",
      "timestamp": null,
      "payload": {
        "text": "Okay, Aaron, here's a summary of the personalized teaching insights, tailored for you as a Senior AI Engineer, along with a Spanish translation:\n\n**Summary:**\n\nAs a Senior AI Engineer, you can use your analytical and problem-solving skills to personalize your teaching. Here are the key points:\n\n1.  **Data-Driven Student Understanding:** Analyze student performance data to identify their strengths and weaknesses, tailoring your methods accordingly. Use formative assessments and track student progress using digital tools or spreadsheets.\n\n2.  **Adaptive Content and Delivery:** Create modular content that can be easily adjusted for different learning needs. Develop a resource repository and experiment with various media to cater to diverse learning preferences.\n\n3.  **Algorithm-Based Feedback:** Provide timely and specific feedback, like debugging code, that pinpoints issues and helps students grow. Use rubrics and automated tools to offer initial feedback, focusing on concepts, not just the answer.\n\n4.  **Collaborative Problem-Solving:** Treat your classroom as an agile team project. Encourage collaboration and peer-to-peer learning through group activities and having students teach each other.\n\n5.  **Iterative Teaching Process:** Regularly evaluate and adjust your teaching methods based on student feedback and data. Be open to experimenting and refining your approach.\n\n**Spanish Translation:**\n\nOkay, Aaron, aquí tienes un resumen de las ideas para la enseñanza personalizada, adaptadas para ti como Ingeniero Senior de IA, junto con una traducción al español:\n\n**Resumen:**\n\nComo Ingeniero Senior de IA, puedes usar tus habilidades analíticas y de resolución de problemas para personalizar tu enseñanza. Aquí están los puntos clave:\n\n1.  **Comprensión de los Estudiantes Basada en Datos:** Analiza los datos de rendimiento de los estudiantes para identificar sus fortalezas y debilidades, adaptando tus métodos en consecuencia. Utiliza evaluaciones formativas y rastrea el progreso de los estudiantes utilizando herramientas digitales u hojas de cálculo.\n\n2.  **Contenido y Entrega Adaptativos:** Crea contenido modular que pueda ajustarse fácilmente a diferentes necesidades de aprendizaje. Desarrolla un repositorio de recursos y experimenta con diversos medios para atender las diferentes preferencias de aprendizaje.\n\n3.  **Retroalimentación Basada en Algoritmos:** Proporciona retroalimentación oportuna y específica, como la depuración de código, que señale los problemas y ayude a los estudiantes a crecer. Utiliza rúbricas y herramientas automatizadas para ofrecer retroalimentación inicial, enfocándote en los conceptos, no solo en la respuesta.\n\n4.  **Resolución de Problemas Colaborativa:** Trata tu clase como un proyecto de equipo ágil. Fomenta la colaboración y el aprendizaje entre pares a través de actividades grupales y haciendo que los estudiantes se enseñen unos a otros.\n\n5.  **Proceso de Enseñanza Iterativo:** Evalúa y ajusta regularmente tus métodos de enseñanza basándote en la retroalimentación de los estudiantes y los datos. Mantente abierto a experimentar y refinar tu enfoque.\n\nLet me know if you need anything else, Aaron.\n"
      }
    }
  ]
}
```
