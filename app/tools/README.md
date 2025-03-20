# How to test the tools:

## Table of Contents

1. [**AVAILABLE DOCUMENT LOADERS FOR DIFFERENT FILE TYPES**](#available-document-loaders-for-different-file-types)

2. [**PAYLOADS FOR TESTING**](#payloads-for-testing)
    - [**Multiple Choice Quiz Generator**](#multiple-choice-quiz-generator)
    - [**Flashcards Generator**](#flashcards-generator)
    - [**Worksheet Generator**](#worksheet-generator)
    - [**Syllabus Generator**](#syllabus-generator)
    - [**AI-Resistant Assignments**](#ai-resistant-assignments)
    - [**Connect with Them**](#connect-with-them)
    - [**Presentation Generator**](#presentation-generator)
    - [**Rubric Generator**](#rubric-generator)
    - [**Lesson Plan Generator**](#lesson-plan-generator)
    - [**Writing Feedback Generator**](#writing-feedback-generator)

## AVAILABLE DOCUMENT LOADERS FOR DIFFERENT FILE TYPES:

| File Type     | Description                     | Function                           |
| ------------- | ------------------------------- | ---------------------------------- |
| PDF           | Portable Document Format        | `load_pdf_documents`               |
| CSV           | Comma-Separated Values          | `load_csv_documents`               |
| TXT           | Plain Text                      | `load_txt_documents`               |
| MD            | Markdown                        | `load_md_documents`                |
| URL           | Web URL                         | `load_url_documents`               |
| Youtube URL   | Youtube URL                     | `summarize_transcript_youtube_url` |
| PPTX          | PowerPoint Presentation         | `load_pptx_documents`              |
| DOCX          | Word Document                   | `load_docx_documents`              |
| XLS           | Excel Spreadsheet               | `load_xls_documents`               |
| XLSX          | Excel Spreadsheet               | `load_xlsx_documents`              |
| XML           | XML Document                    | `load_xml_documents`               |
| Google Docs   | Documents from Google Drive     | `load_gdocs_documents`             |
| Google Sheets | Spreadsheets from Google Drive  | `load_gsheets_documents`           |
| Google Slides | Presentations from Google Drive | `load_gslides_documents`           |
| Google PDFs   | PDFs from Google Drive          | `load_gpdf_documents`              |
| Images        | PNG, JPG, JPEG                  | `generate_concepts_from_img`       |

## PAYLOADS FOR TESTING:

## Multiple Choice Quiz Generator:

## Input Schema:

```python
class MCQArgs(BaseModel):
    topic: str
    n_questions: int
    file_url: str
    file_type: str
    lang: str = "en"
    grade_level: str
    quiz_description: str
```

## Output Schema:

List of `QuizQuestion`:

```python
class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")
```

### PDF:
```json 
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "multiple-choice-quiz-generator",
		"inputs": [
			{
				"name": "topic",
				"value": "Linear Algebra"
			},
			{
				"name": "n_questions",
				"value": 3
			},
			{
				"name": "file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "file_type",
				"value": "pdf"
			},
			{
				"name": "lang",
				"value": "en"
			},
			{
				"name": "grade_level",
				"value": "college"
			},
			{
				"name": "quiz_description",
				"value": "This multiple-choice quiz assesses students' understanding of key concepts in Linear Algebra, focusing on topics related to Linear Regression as covered in the provided document. It tests knowledge of matrix operations, vector spaces, and transformations, ensuring practical application."
			}
		]
	}
}
```

### Structured Data (EXCEL):

```json
{ 
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "tool",
   "tool_data": {
      "tool_id": "multiple-choice-quiz-generator",
      "inputs": [
         {
            "name": "topic",
            "value": "Countries"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://github.com/AaronSosaRamos/mission-flights/raw/main/files-for-test/Free_Test_Data_1MB_XLSX.xlsx"
         },
         {
            "name": "file_type",
            "value": "xlsx"
         },
         {
            "name": "lang",
            "value": "en"
         },
         {
            "name": "grade_level",
            "value": "high school"
         },
         {
            "name": "quiz_description",
            "value": "This multiple-choice quiz evaluates knowledge about different countries, their capitals, populations, and geographical data based on the provided Excel dataset."
         }
      ]
   }
}
```

### Youtube Videos:

```json
{ 
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "tool",
   "tool_data": {
      "tool_id": "multiple-choice-quiz-generator",
      "inputs": [
         {
            "name": "topic",
            "value": "Machine Learning"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
         },
         {
            "name": "file_type",
            "value": "youtube_url"
         },
         {
            "name": "lang",
            "value": "en"
         },
         {
            "name": "grade_level",
            "value": "college"
         },
         {
            "name": "quiz_description",
            "value": "This quiz assesses students' understanding of fundamental machine learning concepts as explained in the provided YouTube video. Topics include supervised learning, unsupervised learning, and neural networks."
         }
      ]
   }
}
```

### Google Drive (GDocs):

```json
{ 
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "tool",
   "tool_data": {
      "tool_id": "multiple-choice-quiz-generator",
      "inputs": [
         {
            "name": "topic",
            "value": "OpenAI"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
         },
         {
            "name": "file_type",
            "value": "gdoc"
         },
         {
            "name": "lang",
            "value": "en"
         },
         {
            "name": "grade_level",
            "value": "college"
         },
         {
            "name": "quiz_description",
            "value": "This quiz evaluates students' comprehension of OpenAI's capabilities, research focus, and AI applications based on the provided Google Doc."
         }
      ]
   }
}
```

### Google Drive (GPDF):

```json
{ 
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "tool",
   "tool_data": {
      "tool_id": "multiple-choice-quiz-generator",
      "inputs": [
         {
            "name": "topic",
            "value": "OpenAI"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://drive.google.com/file/d/1JIZxgX4aLUUl5bHy5SE8OK7Eg9tT1ZkA/view?usp=drive_link"
         },
         {
            "name": "file_type",
            "value": "gpdf"
         },
         {
            "name": "lang",
            "value": "en"
         },
         {
            "name": "grade_level",
            "value": "college"
         },
         {
            "name": "quiz_description",
            "value": "This multiple-choice quiz assesses knowledge of OpenAI’s key research areas, its AI models, and applications in various industries based on the provided PDF."
         }
      ]
   }
}
```

### Images:

```json
{ 
   "user": {
      "id": "string",
      "fullName": "string",
      "email": "string"
   },
   "type": "tool",
   "tool_data": {
      "tool_id": "multiple-choice-quiz-generator",
      "inputs": [
         {
            "name": "topic",
            "value": "AWS Architecture"
         },
         {
            "name": "n_questions",
            "value": 3
         },
         {
            "name": "file_url",
            "value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
         },
         {
            "name": "file_type",
            "value": "img"
         },
         {
            "name": "lang",
            "value": "en"
         },
         {
            "name": "grade_level",
            "value": "college"
         },
         {
            "name": "quiz_description",
            "value": "This quiz tests knowledge of AWS cloud architecture by analyzing and interpreting the provided image, which contains a detailed architectural diagram of AWS services."
         }
      ]
   }
}
```

## Flashcards Generator:

## Input Schema:

```python
class DynamoArgs(BaseModel):
   file_url: str
   file_type: str
   lang: str = "en"
```

## Output Schema:

List of `FlashCard`:

```python
class Flashcard(BaseModel):
    concept: str = Field(description="The concept of the flashcard")
    definition: str = Field(description="The definition of the flashcard")
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "flashcard-generator",
		"inputs": [
			{
				"name": "file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "file_type",
				"value": "pdf"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "flashcard-generator",
		"inputs": [
			{
				"name": "file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "file_type",
				"value": "xml"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "flashcard-generator",
		"inputs": [
			{
				"name": "file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "file_type",
				"value": "youtube_url"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "flashcard-generator",
		"inputs": [
			{
				"name": "file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "flashcard-generator",
		"inputs": [
			{
				"name": "file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "file_type",
				"value": "img"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## Worksheet Generator:

## Input Schema:

```python
class WorksheetGeneratorArgs(BaseModel):
    grade_level: str
    topic: str
    file_url: str
    file_type: str
    lang: str = "en"
```

## Output Schema:

List of Questions:

```json
{
	"fill_in_the_blank": [],
	"open_ended": [],
	"true_false": [],
	"multiple_choice_question": [],
	"relate_concepts": [],
	"math_exercises": []
}
```

```python
#Fill-in-the-blank question type
class QuestionBlank(BaseModel):
    key: str = Field(description="A unique identifier for the blank, starting from 0.")
    value: str = Field(description="The text content to fill in the blank")

class FillInTheBlankQuestion(BaseModel):
    question: str = Field(description="The question text with blanks indicated by placeholders (It must be 5 blank spaces {0}, {1}, {2}, {3}, {4})")
    blanks: List[QuestionBlank] = Field(description="A list of blanks for the question, each with a key and a value")
    word_bank: List[str] = Field(description="A list of the correct texts that fill in the blanks, in random order")
    explanation: str = Field(description="An explanation of why the answers are correct")

#Open-ended question type
class OpenEndedQuestion(BaseModel):
    question: str = Field(description="The open-ended question text")
    answer: str = Field(description="The expected correct answer")
    feedback: List[str] = Field(description="A list of possible answers for the provided question")

#True-False question type
class TrueFalseQuestion(BaseModel):
    question: str = Field(description="The True-False question text")
    answer: bool = Field(description="The correct answer, either True or False")
    explanation: str = Field(description="An explanation of why the answer is correct")

#Multiple Choice question type
class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")
class MultipleChoiceQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")

#Relate concepts question type
class TermMeaningPair(BaseModel):
    term: str = Field(description="The term to be matched")
    meaning: str = Field(description="The meaning of the term")

class RelateConceptsQuestion(BaseModel):
    question: str = Field(..., description="The 'Relate concepts' question text. It must be appropriate for generating pairs and answers.")
    pairs: List[TermMeaningPair] = Field(..., description="A list of term-meaning pairs in disorder. It must not be empty.")
    answer: List[TermMeaningPair] = Field(..., description="A list of the correct term-meaning pairs in order. It must not be empty.")
    explanation: str = Field(..., description="An explanation of the correct term-meaning pairs")

#Math. Exercise question type
class MathExerciseQuestion(BaseModel):
    question: str = Field(description="The math exercise question text")
    solution: str = Field(description="The step-by-step solution to the math problem")
    correct_answer: str = Field(description="The correct answer to the math problem")
    explanation: str = Field(description="An explanation of why the solution is correct")
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "worksheet-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "topic",
				"value": "Machine Learning"
			},
			{
				"name": "file_url",
				"value": "https://www.interactions.com/wp-content/uploads/2017/06/machine_learning_wp-5.pdf"
			},
			{
				"name": "file_type",
				"value": "pdf"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "worksheet-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "topic",
				"value": "Books"
			},
			{
				"name": "file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "file_type",
				"value": "xml"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "worksheet-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "topic",
				"value": "Machine Learning"
			},
			{
				"name": "file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "file_type",
				"value": "youtube_url"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "worksheet-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "topic",
				"value": "OpenAI"
			},
			{
				"name": "file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "worksheet-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "topic",
				"value": "AWS Architecture"
			},
			{
				"name": "file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "file_type",
				"value": "img"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## Syllabus Generator:

## Input Schema:

```python
class SyllabusGeneratorArgsModel(BaseModel):
    grade_level: str
    subject: str
    course_description: str
    objectives: str
    required_materials: str
    grading_policy: str
    policies_expectations: str
    course_outline: str
    additional_notes: str
    file_url: str
    file_type: str
    lang: str = "en"
```

## Output Schema:

```python
class CourseInformation(BaseModel):
    course_title: str = Field(description="The course title")
    grade_level: str = Field(description="The grade level")
    description: str = Field(description="The course description")

class CourseDescriptionObjectives(BaseModel):
    objectives: List[str] = Field(description="The course objectives")
    intended_learning_outcomes: List[str] = Field(description="The intended learning outcomes of the course")

class CourseContentItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course content")
    unit_time_value: int = Field(description="The unit of time value for the course content")
    topic: str = Field(description="The topic per unit of time for the course content")

class PoliciesProcedures(BaseModel):
    attendance_policy: str = Field(description="The attendance policy of the class")
    late_submission_policy: str = Field(description="The late submission policy of the class")
    academic_honesty: str = Field(description="The academic honesty policy of the class")

class AssessmentMethod(BaseModel):
    type_assessment: str = Field(description="The type of assessment")
    weight: int = Field(description="The weight of the assessment in the final grade")

class AssessmentGradingCriteria(BaseModel):
    assessment_methods: List[AssessmentMethod] = Field(description="The assessment methods")
    grading_scale: dict = Field(description="The grading scale")

class LearningResource(BaseModel):
    title: str = Field(description="The book title of the learning resource")
    author: str = Field(description="The book author of the learning resource")
    year: int = Field(description="The year of creation of the book")

class CourseScheduleItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course schedule item")
    unit_time_value: int = Field(description="The unit of time value for the course schedule item")
    date: str = Field(description="The date for the course schedule item")
    topic: str = Field(description="The topic for the learning resource")
    activity_desc: str = Field(description="The descrition of the activity for the learning resource")

class SyllabusSchema(BaseModel):
    course_information: CourseInformation = Field(description="The course information")
    course_description_objectives: CourseDescriptionObjectives = Field(description="The objectives of the course")
    course_content: List[CourseContentItem] = Field(description="The content of the course")
    policies_procedures: PoliciesProcedures = Field(description="The policies procedures of the course")
    assessment_grading_criteria: AssessmentGradingCriteria = Field(description="The asssessment grading criteria of the course")
    learning_resources: List[LearningResource] = Field(description="The learning resources of the course")
    course_schedule: List[CourseScheduleItem] = Field(description="The course schedule")
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "syllabus-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "subject",
				"value": "Linear Regression"
			},
			{
				"name": "course_description",
				"value": "This course introduces Linear Regression concepts, focusing on mathematical foundations and practical applications."
			},
			{
				"name": "objectives",
				"value": "Understand regression theory, perform analysis on datasets, and interpret statistical results."
			},
			{
				"name": "required_materials",
				"value": "Laptop, statistical software (e.g., R, Python), and course textbook."
			},
			{
				"name": "grading_policy",
				"value": "Projects contribute 40%, exams contribute 60%."
			},
			{
				"name": "policies_expectations",
				"value": "Students must submit assignments on time and actively participate in discussions."
			},
			{
				"name": "course_outline",
				"value": "Week 1: Introduction to Linear Regression\nWeek 2: Least Squares Method\nWeek 3: Hypothesis Testing\nWeek 4: Multivariate Regression\nWeek 5: Diagnostics and Residual Analysis\nWeek 6: Regularization Techniques\nWeek 7: Model Validation\nWeek 8: Capstone Project."
			},
			{
				"name": "additional_notes",
				"value": "This course is intensive and requires prior knowledge of basic statistics."
			},
			{
				"name": "file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "file_type",
				"value": "pdf"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "syllabus-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "subject",
				"value": "Software Engineering"
			},
			{
				"name": "course_description",
				"value": "This course covers the principles and practices of software engineering, including requirements analysis, system design, development, testing, and maintenance."
			},
			{
				"name": "objectives",
				"value": "Understand software development life cycles, design scalable systems, and apply testing methodologies to ensure quality software."
			},
			{
				"name": "required_materials",
				"value": "Computer with IDE installed, course textbook on software engineering, and internet access for research."
			},
			{
				"name": "grading_policy",
				"value": "Projects contribute 50%, exams contribute 40%, and participation contributes 10%."
			},
			{
				"name": "policies_expectations",
				"value": "Active participation is required. Assignments must be submitted on time. Collaboration is encouraged, but plagiarism is strictly prohibited."
			},
			{
				"name": "course_outline",
				"value": "Week 1: Introduction to Software Engineering\nWeek 2: Requirements Engineering\nWeek 3: System Design and Architecture\nWeek 4: Implementation and Coding Standards\nWeek 5: Testing and Debugging Techniques\nWeek 6: Agile and DevOps Practices\nWeek 7: Software Maintenance\nWeek 8: Capstone Project."
			},
			{
				"name": "additional_notes",
				"value": "This course requires prior knowledge of basic programming concepts."
			},
			{
				"name": "file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "file_type",
				"value": "xml"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "syllabus-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "subject",
				"value": "Machine Learning"
			},
			{
				"name": "course_description",
				"value": "This course introduces the fundamental concepts and techniques of machine learning, including supervised and unsupervised learning, model evaluation, and practical applications using modern tools."
			},
			{
				"name": "objectives",
				"value": "Understand the theoretical foundations of machine learning algorithms, apply them to real-world datasets, and evaluate model performance effectively."
			},
			{
				"name": "required_materials",
				"value": "Computer with Python installed, Jupyter Notebook, and a stable internet connection for accessing datasets and libraries."
			},
			{
				"name": "grading_policy",
				"value": "Projects contribute 50%, exams contribute 40%, and participation contributes 10%."
			},
			{
				"name": "policies_expectations",
				"value": "Students are expected to complete weekly assignments, participate in discussions, and adhere to academic honesty policies."
			},
			{
				"name": "course_outline",
				"value": "Week 1: Introduction to Machine Learning\nWeek 2: Linear Regression and Classification\nWeek 3: Decision Trees and Random Forests\nWeek 4: Support Vector Machines\nWeek 5: Neural Networks\nWeek 6: Unsupervised Learning and Clustering\nWeek 7: Model Evaluation and Optimization\nWeek 8: Capstone Project."
			},
			{
				"name": "additional_notes",
				"value": "Familiarity with basic statistics and programming is recommended."
			},
			{
				"name": "file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "file_type",
				"value": "youtube_url"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "syllabus-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "subject",
				"value": "LLMs"
			},
			{
				"name": "course_description",
				"value": "This course delves into the foundations, architectures, and applications of Large Language Models (LLMs). Students will explore key topics including transformer models, pretraining techniques, fine-tuning strategies, and practical use cases in natural language processing (NLP)."
			},
			{
				"name": "objectives",
				"value": "Understand the theory and architecture of LLMs, implement fine-tuning for specific tasks, and critically evaluate their performance and limitations."
			},
			{
				"name": "required_materials",
				"value": "Laptop with Python installed, access to popular libraries like TensorFlow or PyTorch, and a stable internet connection for experimenting with APIs like OpenAI or Hugging Face."
			},
			{
				"name": "grading_policy",
				"value": "Projects contribute 50%, exams contribute 40%, and participation contributes 10%."
			},
			{
				"name": "policies_expectations",
				"value": "Students must actively engage in discussions, complete weekly assignments, and ensure academic honesty throughout the course."
			},
			{
				"name": "course_outline",
				"value": "Week 1: Introduction to LLMs and Transformers\nWeek 2: Pretraining and Fine-Tuning\nWeek 3: Applications of LLMs in NLP\nWeek 4: Ethical Implications and Bias in LLMs\nWeek 5: Advanced Architectures (e.g., GPT, BERT)\nWeek 6: Scaling LLMs and Distributed Computing\nWeek 7: Evaluation Metrics for LLMs\nWeek 8: Capstone Project: Building and Deploying an LLM."
			},
			{
				"name": "additional_notes",
				"value": "Familiarity with basic machine learning concepts and programming is recommended."
			},
			{
				"name": "file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "syllabus-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "subject",
				"value": "AWS Architectures"
			},
			{
				"name": "course_description",
				"value": "This course provides an in-depth understanding of AWS architectures and best practices for designing scalable, secure, and cost-effective solutions on the Amazon Web Services (AWS) cloud platform. Students will explore topics like compute, storage, databases, and networking within AWS."
			},
			{
				"name": "objectives",
				"value": "Learn to design scalable and resilient AWS architectures, implement best practices for security and cost management, and deploy AWS solutions for real-world applications."
			},
			{
				"name": "required_materials",
				"value": "Laptop with internet access, AWS free-tier account, and course-provided materials."
			},
			{
				"name": "grading_policy",
				"value": "Projects contribute 60%, exams contribute 30%, and participation contributes 10%."
			},
			{
				"name": "policies_expectations",
				"value": "Students must complete weekly labs and assignments, actively participate in discussions, and comply with AWS cloud usage policies."
			},
			{
				"name": "course_outline",
				"value": "Week 1: Introduction to AWS Cloud Computing\nWeek 2: Compute Services and EC2\nWeek 3: Storage Solutions (S3, EBS, Glacier)\nWeek 4: Networking and Content Delivery\nWeek 5: Databases and AWS RDS\nWeek 6: Security Best Practices\nWeek 7: Monitoring and Optimization\nWeek 8: Capstone Project: Building a Scalable AWS Architecture."
			},
			{
				"name": "additional_notes",
				"value": "Prior knowledge of basic cloud computing concepts is recommended."
			},
			{
				"name": "file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2023/02/13/adverse_1-1024x546.png"
			},
			{
				"name": "file_type",
				"value": "img"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## AI-Resistant Assignments

## Input Schema:

```python
class AIResistantArgs(BaseModel):
    grade_level: Literal["pre-k", "kindergarten", "elementary", "middle", "high", "university", "professional"]
    assignment_description: str
    file_type: str
    file_url: str
    lang: str
```

## Output Schema:

```python
class AIResistanceIdea(BaseModel):
    title: str = Field(..., description="The main title of the idea")
    assignment_description: str = Field(..., description="Detailed description of the modified assignment")
    explanation: str = Field(..., description="Explanation of how this modification makes the assignment AI-resistant")

class AIResistantOutput(BaseModel):
    topic: str = Field(..., description="Topic or subject related to the assignment")
    grade_level: str = Field(..., description="Educational level to which the assignment is directed")
    ideas: List[AIResistanceIdea] = Field(..., description="List of 3 ideas to make the assignment AI-resistant, including explanation")
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "ai-resistant-assignments-generator",
		"inputs": [
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "file_type",
				"value": "pdf"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "ai-resistant-assignments-generator",
		"inputs": [
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "file_type",
				"value": "xml"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "ai-resistant-assignments-generator",
		"inputs": [
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "file_type",
				"value": "youtube_url"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "ai-resistant-assignments-generator",
		"inputs": [
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "ai-resistant-assignments-generator",
		"inputs": [
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "file_type",
				"value": "img"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## Connect with Them

## Input Schema:

```python
class ConnectWithThemArgs(BaseModel):
    grade_level: str
    task_description: str
    students_description: str
    task_description_file_url: str
    task_description_file_type: str
    student_description_file_url: str
    student_description_file_type: str
    lang: str
```

## Output Schema:

```python
class Recommendation(BaseModel):
    title: str = Field(..., description="The title of the recommendation")
    project_overview: str = Field(..., description="A detailed description of the project or activity recommendation. It must be a large paragraph.")
    rationale: str = Field(..., description="An explanation of why this recommendation is relevant to the students' interests or background.")
    difficulty_level: str = Field(..., description="The difficulty level of the project (e.g., easy, moderate, challenging).")
    required_tools: List[str] = Field(..., description="A list of tools, software, or resources required to complete the project.")
    estimated_time: str = Field(..., description="The estimated time to complete the project or activity.")

class RecommendationsOutput(BaseModel):
    recommendations: List[Recommendation] = Field(..., description="A list of personalized recommendations based on the input.")
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "connect-with-them",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "task_description",
				"value": ""
			},
			{
				"name": "students_description",
				"value": ""
			},
			{
				"name": "task_description_file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "task_description_file_type",
				"value": "pdf"
			},
			{
				"name": "student_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "student_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "connect-with-them",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "task_description",
				"value": ""
			},
			{
				"name": "students_description",
				"value": ""
			},
			{
				"name": "task_description_file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "task_description_file_type",
				"value": "xml"
			},
			{
				"name": "student_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "student_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "connect-with-them",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "task_description",
				"value": ""
			},
			{
				"name": "students_description",
				"value": ""
			},
			{
				"name": "task_description_file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "task_description_file_type",
				"value": "youtube_url"
			},
			{
				"name": "student_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "student_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "connect-with-them",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "task_description",
				"value": ""
			},
			{
				"name": "students_description",
				"value": ""
			},
			{
				"name": "task_description_file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "task_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "student_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "student_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "connect-with-them",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "task_description",
				"value": ""
			},
			{
				"name": "students_description",
				"value": ""
			},
			{
				"name": "task_description_file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "task_description_file_type",
				"value": "img"
			},
			{
				"name": "student_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "student_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## Presentation Generator

## Input Schema:

```python
class PresentationGeneratorInput(BaseModel):
    grade_level: str
    n_slides: int
    topic: str
    objectives: str
    additional_comments: str
    objectives_file_url: str #Standards/Objectives File URL
    objectives_file_type: str #Standards/Objectives File Type
    additional_comments_file_url: str
    additional_comments_file_type: str
    lang: str = "en"
```

## Output Schema:

```python
class Slide(BaseModel):
    title: str = Field(..., description="The title of the Slide")
    content: str = Field(..., description="The content of the Slide. It must be the actual context, not simple indications")
    suggestions: str = Field(..., description="""Suggestions for visual elements (e.g., charts, images, layouts)
                             that enhance understanding and engagement (ONLY IF NEEDED).""")

class FullPresentation(BaseModel):
    main_title: str = Field(..., description="The main title of the Presentation")
    list_slides: List[Slide] = Field(..., description="The full collection of slides about the Presentation")
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "presentation-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "n_slides",
				"value": 9
			},
			{
				"name": "topic",
				"value": "Linear Algebra"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_comments",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "objectives_file_type",
				"value": "pdf"
			},
			{
				"name": "additional_comments_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_comments_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "presentation-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "n_slides",
				"value": 9
			},
			{
				"name": "topic",
				"value": "Software Engineering Book"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_comments",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "objectives_file_type",
				"value": "xml"
			},
			{
				"name": "additional_comments_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_comments_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "presentation-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "n_slides",
				"value": 9
			},
			{
				"name": "topic",
				"value": "Machine Learning"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_comments",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "objectives_file_type",
				"value": "youtube_url"
			},
			{
				"name": "additional_comments_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_comments_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "presentation-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "n_slides",
				"value": 9
			},
			{
				"name": "topic",
				"value": "OpenAI"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_comments",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "objectives_file_type",
				"value": "gdoc"
			},
			{
				"name": "additional_comments_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_comments_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "presentation-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "n_slides",
				"value": 9
			},
			{
				"name": "topic",
				"value": "AWS Architecture"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_comments",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "objectives_file_type",
				"value": "img"
			},
			{
				"name": "additional_comments_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_comments_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## Rubric Generator

## Input Schema:

```python
class RubricGeneratorArgs(BaseModel):
    grade_level: Literal["pre-k", "kindergarten", "elementary", "middle", "high", "university", "professional"]
    point_scale: int
    objectives: str
    assignment_description: str
    objectives_file_url: str #Standards/Objectives File URL
    objectives_file_type: str #Standards/Objectives File Type
    assignment_description_file_url: str #Assignment Description File URL
    assignment_description_file_type: str
    lang: str
```

## Output Schema:

```python
class CriteriaDescription(BaseModel):
    points: str = Field(..., description="The total points gained by the student according to the point_scale an the level name")
    description: List[str] = Field(..., description="Description for the specific point on the scale")

class RubricCriteria(BaseModel):
    criteria: str = Field(..., description="name of the criteria in the rubric")
    criteria_description: List[CriteriaDescription] = Field(..., description="Descriptions for each point on the scale")

class RubricOutput(BaseModel):
    title: str = Field(..., description="the rubric title of the assignment based on the standard input parameter")
    grade_level: str = Field(..., description="The grade level for which the rubric is created")
    criterias: List[RubricCriteria] = Field(..., description="The grading criteria for the rubric")
    feedback: str = Field(..., description="the feedback provided by the AI model on the generated rubric")
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "rubric-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "point_scale",
				"value": 4
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "objectives_file_type",
				"value": "pdf"
			},
			{
				"name": "assignment_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "assignment_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "rubric-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "point_scale",
				"value": 4
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "objectives_file_type",
				"value": "xml"
			},
			{
				"name": "assignment_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "assignment_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "rubric-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "point_scale",
				"value": 4
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "objectives_file_type",
				"value": "youtube_url"
			},
			{
				"name": "assignment_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "assignment_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "rubric-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "point_scale",
				"value": 4
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "objectives_file_type",
				"value": "gdoc"
			},
			{
				"name": "assignment_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "assignment_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "chat",
	"tool_data": {
		"tool_id": "rubric-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "point_scale",
				"value": 4
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "assignment_description",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "objectives_file_type",
				"value": "img"
			},
			{
				"name": "assignment_description_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "assignment_description_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## Lesson Plan Generator

## Input Schema:

```python
class LessonPlanGeneratorArgs(BaseModel):
    grade_level: str
    topic: str
    objectives: str
    additional_customization: str
    objectives_file_url: str #Standards/Objectives File URL
    objectives_file_type: str #Standards/Objectives File Type
    additional_customization_file_url: str
    additional_customization_file_type: str
    lang: str = "en"
```

## Output Schema:

```python
class Title(BaseModel):
    title: str

class Objective(BaseModel):
    objective: str

class Assessment(BaseModel):
    assessment: str

class KeyPoint(BaseModel):
    title: str
    description: str

class Section(BaseModel):
    title: str
    content: List[str]

class IndependentPractice(BaseModel):
    description: str
    tasks: List[str]

class ExtensionActivity(BaseModel):
    description: str
    additional_instructions: Optional[str]

class Homework(BaseModel):
    description: str
    submission_instructions: Optional[str]

class Standard(BaseModel):
    name: str
    description: str

class KeyPoints(BaseModel):
    key_points: List[KeyPoint]

class StandardsAddressed(BaseModel):
    standards_addressed: List[Standard]

class LessonPlan(BaseModel):
    title: Title
    objective: Objective
    assessment: Assessment
    key_points: KeyPoints
    opening: Section
    introduction_to_new_material: Section
    guided_practice: Section
    independent_practice: IndependentPractice
    closing: Section
    extension_activity: ExtensionActivity
    homework: Homework
    standards_addressed: StandardsAddressed
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "lesson-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "topic",
				"value": "Linear Algebra"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_customization",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "objectives_file_type",
				"value": "pdf"
			},
			{
				"name": "additional_customization_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_customization_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "lesson-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "topic",
				"value": "Software Engineering Book"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_customization",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "objectives_file_type",
				"value": "xml"
			},
			{
				"name": "additional_customization_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_customization_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "lesson-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "topic",
				"value": "Machine Learning"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_customization",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "objectives_file_type",
				"value": "youtube_url"
			},
			{
				"name": "additional_customization_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_customization_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "lesson-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "topic",
				"value": "OpenAI"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_customization",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "objectives_file_type",
				"value": "gdoc"
			},
			{
				"name": "additional_customization_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_customization_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "lesson-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "topic",
				"value": "AWS Architecture"
			},
			{
				"name": "objectives",
				"value": ""
			},
			{
				"name": "additional_customization",
				"value": ""
			},
			{
				"name": "objectives_file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "objectives_file_type",
				"value": "img"
			},
			{
				"name": "additional_customization_file_url",
				"value": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true"
			},
			{
				"name": "additional_customization_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

## Writing Feedback Generator

## Input Schema:

```python
class WritingFeedbackGeneratorArgs(BaseModel):
    grade_level: str
    assignment_description: str
    criteria: str
    writing_to_review: str
    criteria_file_url: str #Criteria File URL
    criteria_file_type: str #Criteria File Type
    writing_to_review_file_url: str
    writing_to_review_file_type: str
    lang: str = "en"
```

## Output Schema:

```python
class FeedbackSection(BaseModel):
    title: str
    points: List[str]

class WritingFeedback(BaseModel):
    title: str
    areas_of_strength: FeedbackSection
    areas_for_growth: FeedbackSection
    general_feedback: FeedbackSection
```

### PDF:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "writing-feedback-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "assignment_description",
				"value": "Linear Algebra"
			},
			{
				"name": "criteria",
				"value": "Understand the concepts of vector spaces, linear transformations, and matrix operations."
			},
			{
				"name": "writing_to_review",
				"value": ""
			},
			{
				"name": "criteria_file_url",
				"value": ""
			},
			{
				"name": "criteria_file_type",
				"value": ""
			},
			{
				"name": "writing_to_review_file_url",
				"value": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
			},
			{
				"name": "writing_to_review_file_type",
				"value": "pdf"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Structured Data (XML):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "writing-feedback-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "College"
			},
			{
				"name": "assignment_description",
				"value": "Software Engineering Book"
			},
			{
				"name": "criteria",
				"value": "Understand software development life cycles and methodologies."
			},
			{
				"name": "writing_to_review",
				"value": ""
			},
			{
				"name": "criteria_file_url",
				"value": ""
			},
			{
				"name": "criteria_file_type",
				"value": ""
			},
			{
				"name": "writing_to_review_file_url",
				"value": "https://raw.githubusercontent.com/AaronSosaRamos/mission-flights/main/files-for-test/sample.xml"
			},
			{
				"name": "writing_to_review_file_type",
				"value": "xml"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Youtube Videos:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "writing-feedback-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "assignment_description",
				"value": "Machine Learning"
			},
			{
				"name": "criteria",
				"value": "Understand the basics of machine learning algorithms."
			},
			{
				"name": "writing_to_review",
				"value": ""
			},
			{
				"name": "criteria_file_url",
				"value": ""
			},
			{
				"name": "criteria_file_type",
				"value": ""
			},
			{
				"name": "writing_to_review_file_url",
				"value": "https://www.youtube.com/watch?v=HgBpFaATdoA"
			},
			{
				"name": "writing_to_review_file_type",
				"value": "youtube_url"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Google Drive (GDocs):

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "writing-feedback-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "assignment_description",
				"value": "OpenAI"
			},
			{
				"name": "criteria",
				"value": "Explore the advancements in artificial intelligence by OpenAI."
			},
			{
				"name": "writing_to_review",
				"value": ""
			},
			{
				"name": "criteria_file_url",
				"value": ""
			},
			{
				"name": "criteria_file_type",
				"value": ""
			},
			{
				"name": "writing_to_review_file_url",
				"value": "https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link"
			},
			{
				"name": "writing_to_review_file_type",
				"value": "gdoc"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```

### Images:

```json
{
	"user": {
		"id": "string",
		"fullName": "string",
		"email": "string"
	},
	"type": "tool",
	"tool_data": {
		"tool_id": "writing-feedback-generator",
		"inputs": [
			{
				"name": "grade_level",
				"value": "university"
			},
			{
				"name": "assignment_description",
				"value": "AWS Architecture"
			},
			{
				"name": "criteria",
				"value": "Understand the components and services in AWS architecture."
			},
			{
				"name": "writing_to_review",
				"value": ""
			},
			{
				"name": "criteria_file_url",
				"value": ""
			},
			{
				"name": "criteria_file_type",
				"value": ""
			},
			{
				"name": "writing_to_review_file_url",
				"value": "https://d2908q01vomqb2.cloudfront.net/fc074d501302eb2b93e2554793fcaf50b3bf7291/2022/04/22/586-P2-Fig-1-1024x538.png"
			},
			{
				"name": "writing_to_review_file_type",
				"value": "img"
			},
			{
				"name": "lang",
				"value": "en"
			}
		]
	}
}
```
