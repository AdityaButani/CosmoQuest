import os
import requests
import json
import logging
from typing import Dict, Optional, Any

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
SERPER_API_URL = "https://google.serper.dev/search"

def search_topic_context(topic: str) -> str:
    """Search for additional context about the topic using SerperAPI"""
    try:
        if not SERPER_API_KEY:
            logging.warning("SERPER_API_KEY not found, skipping web search")
            return f"Learn about {topic}"
        
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': f"{topic} explanation education learning",
            'num': 5
        }
        
        response = requests.post(SERPER_API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant information from search results
            context_parts = []
            
            if 'organic' in data:
                for result in data['organic'][:3]:  # Top 3 results
                    if 'snippet' in result:
                        context_parts.append(result['snippet'])
            
            if 'answerBox' in data and 'answer' in data['answerBox']:
                context_parts.insert(0, data['answerBox']['answer'])
            
            return ' '.join(context_parts) if context_parts else f"Learn about {topic}"
        else:
            logging.error(f"SerperAPI error: {response.status_code}")
            return f"Learn about {topic}"
            
    except Exception as e:
        logging.error(f"Error searching topic context: {str(e)}")
        return f"Learn about {topic}"

def generate_quest_content(topic: str, quest_num: int, context: str = "") -> Optional[Dict[str, Any]]:
    """Generate quest content using Groq API"""
    try:
        if not GROQ_API_KEY:
            logging.error("GROQ_API_KEY not found")
            return None
        
        # Define quest specifications
        quest_specs = {
            1: {
                "title": "Introduction & Overview",
                "description": "Basic introduction to the topic",
                "has_quiz": False
            },
            2: {
                "title": "Fundamental Concepts",
                "description": "Expanded explanation with key concepts",
                "has_quiz": True,
                "quiz_type": "true_false",
                "quiz_count": 5
            },
            3: {
                "title": "Deeper Understanding",
                "description": "Advanced concepts and relationships",
                "has_quiz": True,
                "quiz_type": "matching",
                "quiz_count": 5
            },
            4: {
                "title": "Practical Applications",
                "description": "Real-world applications and examples",
                "has_quiz": True,
                "quiz_type": "multiple_choice",
                "quiz_count": 5
            },
            5: {
                "title": "Mastery & Integration",
                "description": "Comprehensive review and advanced insights",
                "has_quiz": True,
                "quiz_type": "mixed",
                "quiz_count": 10
            }
        }
        
        spec = quest_specs[quest_num]
        
        # Construct the prompt
        system_prompt = f"""You are an expert educational content creator. Create engaging, accurate, and well-structured learning content for Quest {quest_num} of 5 about "{topic}".

Context from web search: {context}

Quest {quest_num}: {spec['title']}
{spec['description']}

Generate a JSON response with the following structure:
{{
    "title": "Quest {quest_num}: {spec['title']}",
    "content": "Detailed educational content (2-3 paragraphs, engaging and informative)",
    "key_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
    "fun_facts": ["Interesting fact 1", "Interesting fact 2", "Interesting fact 3"],
    "visual_suggestions": ["Description of helpful diagram/chart 1", "Description of helpful visual 2"],
    "resources": [
        {{"title": "Resource 1", "url": "https://example1.com", "description": "Brief description"}},
        {{"title": "Resource 2", "url": "https://example2.com", "description": "Brief description"}}
    ]"""

        if spec["has_quiz"]:
            if spec["quiz_type"] == "true_false":
                system_prompt += f""",
    "quiz": {{
        "type": "true_false",
        "instructions": "Select True or False for each statement",
        "questions": [
            {{"id": "q1", "question": "Statement 1", "type": "true_false"}},
            {{"id": "q2", "question": "Statement 2", "type": "true_false"}},
            {{"id": "q3", "question": "Statement 3", "type": "true_false"}},
            {{"id": "q4", "question": "Statement 4", "type": "true_false"}},
            {{"id": "q5", "question": "Statement 5", "type": "true_false"}}
        ],
        "correct_answers": {{"q1": "true", "q2": "false", "q3": "true", "q4": "false", "q5": "true"}}
    }}"""
            elif spec["quiz_type"] == "matching":
                system_prompt += f""",
    "quiz": {{
        "type": "matching",
        "instructions": "Match each term with its correct definition",
        "questions": [
            {{"id": "q1", "question": "Term 1", "options": ["Definition A", "Definition B", "Definition C", "Definition D"], "type": "matching"}},
            {{"id": "q2", "question": "Term 2", "options": ["Definition A", "Definition B", "Definition C", "Definition D"], "type": "matching"}},
            {{"id": "q3", "question": "Term 3", "options": ["Definition A", "Definition B", "Definition C", "Definition D"], "type": "matching"}},
            {{"id": "q4", "question": "Term 4", "options": ["Definition A", "Definition B", "Definition C", "Definition D"], "type": "matching"}},
            {{"id": "q5", "question": "Term 5", "options": ["Definition A", "Definition B", "Definition C", "Definition D"], "type": "matching"}}
        ],
        "correct_answers": {{"q1": "Definition A", "q2": "Definition B", "q3": "Definition C", "q4": "Definition D", "q5": "Definition A"}}
    }}"""
            elif spec["quiz_type"] == "multiple_choice":
                system_prompt += f""",
    "quiz": {{
        "type": "multiple_choice",
        "instructions": "Select the best answer for each question",
        "questions": [
            {{"id": "q1", "question": "Question 1", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}},
            {{"id": "q2", "question": "Question 2", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}},
            {{"id": "q3", "question": "Question 3", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}},
            {{"id": "q4", "question": "Question 4", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}},
            {{"id": "q5", "question": "Question 5", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}}
        ],
        "correct_answers": {{"q1": "Option A", "q2": "Option B", "q3": "Option C", "q4": "Option D", "q5": "Option A"}}
    }}"""
            elif spec["quiz_type"] == "mixed":
                system_prompt += f""",
    "quiz": {{
        "type": "mixed",
        "instructions": "Answer all questions - mix of True/False, Matching, and Multiple Choice",
        "questions": [
            {{"id": "q1", "question": "True/False Statement 1", "type": "true_false"}},
            {{"id": "q2", "question": "True/False Statement 2", "type": "true_false"}},
            {{"id": "q3", "question": "True/False Statement 3", "type": "true_false"}},
            {{"id": "q4", "question": "Match Term 1", "options": ["Definition A", "Definition B", "Definition C"], "type": "matching"}},
            {{"id": "q5", "question": "Match Term 2", "options": ["Definition A", "Definition B", "Definition C"], "type": "matching"}},
            {{"id": "q6", "question": "Match Term 3", "options": ["Definition A", "Definition B", "Definition C"], "type": "matching"}},
            {{"id": "q7", "question": "MCQ Question 1", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}},
            {{"id": "q8", "question": "MCQ Question 2", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}},
            {{"id": "q9", "question": "MCQ Question 3", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}},
            {{"id": "q10", "question": "MCQ Question 4", "options": ["Option A", "Option B", "Option C", "Option D"], "type": "multiple_choice"}}
        ],
        "correct_answers": {{"q1": "true", "q2": "false", "q3": "true", "q4": "Definition A", "q5": "Definition B", "q6": "Definition C", "q7": "Option A", "q8": "Option B", "q9": "Option C", "q10": "Option D"}}
    }}"""

        system_prompt += "\n}\n\nEnsure all content is accurate, educational, and appropriate for the quest level. Make the content engaging and progressive."

        headers = {
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": f"Create Quest {quest_num} content for the topic: {topic}"
                }
            ],
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 1,
            "stream": False
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            
            # Try to parse JSON response
            try:
                quest_data = json.loads(content)
                return quest_data
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic structure
                logging.error(f"Failed to parse JSON from Groq response for quest {quest_num}")
                return create_fallback_quest_content(topic, quest_num, spec)
        else:
            logging.error(f"Groq API error: {response.status_code} - {response.text}")
            return create_fallback_quest_content(topic, quest_num, spec)
            
    except Exception as e:
        logging.error(f"Error generating quest content: {str(e)}")
        return create_fallback_quest_content(topic, quest_num, quest_specs[quest_num])

def create_fallback_quest_content(topic: str, quest_num: int, spec: Dict) -> Dict[str, Any]:
    """Create fallback content when API fails"""
    content = {
        "title": f"Quest {quest_num}: {spec['title']}",
        "content": f"Welcome to Quest {quest_num} about {topic}. This quest focuses on {spec['description'].lower()}. We'll explore the key concepts, understand the fundamentals, and build your knowledge step by step.",
        "key_points": [
            f"Understanding {topic} basics",
            f"Key concepts in {topic}",
            f"Important principles of {topic}",
            f"Applications of {topic}",
            f"Advanced aspects of {topic}"
        ],
        "fun_facts": [
            f"Did you know that {topic} has fascinating applications?",
            f"The study of {topic} reveals interesting patterns.",
            f"Experts in {topic} continue to make new discoveries."
        ],
        "visual_suggestions": [
            f"Conceptual diagram showing {topic} overview",
            f"Flowchart illustrating {topic} processes"
        ],
        "resources": [
            {"title": "Educational Resource", "url": "https://khan-academy.org", "description": "Comprehensive learning materials"},
            {"title": "Reference Material", "url": "https://wikipedia.org", "description": "Detailed reference information"}
        ]
    }
    
    if spec.get("has_quiz"):
        content["quiz"] = create_fallback_quiz(topic, spec)
    
    return content

def create_fallback_quiz(topic: str, spec: Dict) -> Dict[str, Any]:
    """Create a simple fallback quiz when API fails"""
    quiz_type = spec.get("quiz_type", "true_false")
    
    if quiz_type == "true_false":
        return {
            "type": "true_false",
            "instructions": "Select True or False for each statement",
            "questions": [
                {"id": "q1", "question": f"{topic} is an important subject to study.", "type": "true_false"},
                {"id": "q2", "question": f"Learning about {topic} requires no effort.", "type": "true_false"},
                {"id": "q3", "question": f"{topic} has practical applications.", "type": "true_false"},
                {"id": "q4", "question": f"Understanding {topic} is impossible.", "type": "true_false"},
                {"id": "q5", "question": f"{topic} concepts build upon each other.", "type": "true_false"}
            ],
            "correct_answers": {"q1": "true", "q2": "false", "q3": "true", "q4": "false", "q5": "true"}
        }
    
    # Add other quiz types as needed
    return {
        "type": quiz_type,
        "instructions": "Complete the quiz questions",
        "questions": [],
        "correct_answers": {}
    }
