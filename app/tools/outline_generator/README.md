
# Outline Generator Tool

## Overview

The Outline Generator Tool creates structured outlines for educational presentations based on user-provided context, educational level, and desired number of slides.

## Features

- Generates slide outlines tailored to specific educational levels (Elementary, Middle School, High School, University)
- Creates a coherent flow from introduction to conclusion
- Supports external document analysis for additional context
- Produces exactly the requested number of slides
- Returns results in a clean JSON format

## Usage

The tool accepts the following parameters:

- `context`: The topic or subject for the outline (e.g., "World War II overview")
- `num_slides`: Number of slides to generate (e.g., 5, 10, 15, 20)
- `level`: Instructional level (e.g., "Elementary", "High School", "University")
- `file_url`: (Optional) URL of a file with additional context
- `file_type`: (Optional) Type of the file (e.g., "pdf", "txt", "docx")
- `lang`: (Optional) Language for the outline, defaults to "en"

## Response Format

The tool returns a JSON object with a `slides` array containing the slide titles:

```json
{
  "slides": [
    "Introduction to World War II: Global Conflict 1939-1945",
    "Causes and Tensions: The Road to War",
    "Major Combatants and Alliances",
    "Key Battles and Turning Points",
    "The Holocaust: Genocide and Persecution",
    "Technology and Warfare Advancements",
    "Home Fronts and Civilian Experiences",
    "The Pacific Theater: War in Asia",
    "D-Day and the Liberation of Europe",
    "Aftermath and Shaping the Modern World"
  ]
}
```

## Example

Request:
```
{
  "context": "World War II overview",
  "num_slides": 10,
  "level": "High School"
}
```

The tool processes this request using Gemini AI and returns a structured outline appropriate for high school students with exactly 10 slides.
