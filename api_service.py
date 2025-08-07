import os
import requests
import json
import logging
from typing import Dict, Optional, Any

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
SERPER_API_URL = "https://google.serper.dev/search"
SERPER_IMAGES_URL = "https://google.serper.dev/images"

def search_images_for_visual_aid(query: str, topic: str) -> list:
    """Search for educational images using SerperAPI"""
    try:
        if not SERPER_API_KEY:
            logging.warning("SERPER_API_KEY not found, skipping image search")
            return []
        
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Create educational-focused search query
        search_query = f"{topic} {query} educational diagram illustration"
        
        payload = {
            'q': search_query,
            'num': 6,  # Get more images to filter better ones
            'safe': 'active'  # Ensure safe content for educational use
        }
        
        response = requests.post(SERPER_IMAGES_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            images = []
            
            if 'images' in data:
                for img in data['images'][:3]:  # Top 3 relevant images
                    if 'imageUrl' in img and 'title' in img:
                        # Filter for educational and appropriate images
                        title = img.get('title', '').lower()
                        
                        # Skip inappropriate or non-educational content
                        if any(skip_word in title for skip_word in ['meme', 'funny', 'joke', 'cartoon']):
                            continue
                            
                        # Prefer educational sources
                        source = img.get('source', '').lower()
                        is_educational = any(edu_source in source for edu_source in [
                            'wikipedia', 'edu', 'academic', 'university', 'britannica', 
                            'khan', 'coursera', 'edx', 'mit', 'stanford'
                        ])
                        
                        images.append({
                            'url': img['imageUrl'],
                            'title': img.get('title', query),
                            'source': img.get('source', 'Educational Resource'),
                            'educational': is_educational
                        })
                        
                        if len(images) >= 2:  # Limit to 2 images per visual aid
                            break
            
            # Sort by educational value
            images.sort(key=lambda x: x['educational'], reverse=True)
            return images[:2]  # Return top 2 images
            
        else:
            logging.error(f"SerperAPI Images error: {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error searching for images: {str(e)}")
        return []

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

def enrich_visual_suggestions_with_images(quest_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
    """Enrich visual suggestions with actual images from SerperAPI"""
    try:
        if 'visual_suggestions' not in quest_data or not quest_data['visual_suggestions']:
            return quest_data
        
        enriched_suggestions = []
        
        for suggestion in quest_data['visual_suggestions']:
            # Create an enriched visual suggestion with images
            enriched_suggestion = {
                'description': suggestion,
                'images': []
            }
            
            # Search for images related to this visual suggestion
            images = search_images_for_visual_aid(suggestion, topic)
            
            if images:
                enriched_suggestion['images'] = images
                logging.info(f"Found {len(images)} images for visual suggestion: {suggestion}")
            else:
                logging.warning(f"No images found for visual suggestion: {suggestion}")
            
            enriched_suggestions.append(enriched_suggestion)
        
        # Replace the simple text suggestions with enriched ones
        quest_data['visual_suggestions'] = enriched_suggestions
        
        return quest_data
        
    except Exception as e:
        logging.error(f"Error enriching visual suggestions with images: {str(e)}")
        # Return original quest_data if enrichment fails
        return quest_data

def generate_quest_content(topic: str, quest_num: int, context: str = "") -> Optional[Dict[str, Any]]:
    """Generate quest content using Groq API"""
    try:
        if not GROQ_API_KEY:
            logging.error("GROQ_API_KEY not found")
            return None
        
        # Define quest specifications with distinct, non-overlapping content areas
        quest_specs = {
            1: {
                "title": "Foundations & Core Principles",
                "content_focus": "Basic definitions, historical background, fundamental principles, and why this topic matters",
                "has_quiz": False
            },
            2: {
                "title": "Mechanisms & Processes", 
                "content_focus": "How it works step-by-step, underlying mechanisms, key processes, and scientific principles",
                "has_quiz": True,
                "quiz_type": "true_false",
                "quiz_count": 5
            },
            3: {
                "title": "Advanced Systems & Interactions",
                "content_focus": "Complex relationships, advanced techniques, system interactions, and specialized methods",
                "has_quiz": True,
                "quiz_type": "multiple_choice", 
                "quiz_count": 5
            },
            4: {
                "title": "Real-World Applications & Impact",
                "content_focus": "Practical applications, industry uses, societal impact, and problem-solving approaches",
                "has_quiz": True,
                "quiz_type": "multiple_choice",
                "quiz_count": 5
            },
            5: {
                "title": "Innovations & Future Directions",
                "content_focus": "Latest research, emerging trends, future possibilities, and cutting-edge developments",
                "has_quiz": True,
                "quiz_type": "mixed",
                "quiz_count": 10
            }
        }
        
        spec = quest_specs[quest_num]
        
        # Construct the prompt with distinct content focus for each quest
        system_prompt = f"""You are an expert educational content creator. Create comprehensive, specialized learning content for Quest {quest_num} of 5 about "{topic}".

Context from web search: {context}

Quest {quest_num}: {spec['title']}
SPECIFIC CONTENT FOCUS: {spec['content_focus']}

CRITICAL: Each quest must cover COMPLETELY DIFFERENT aspects of {topic}. DO NOT repeat content from other quests.

Quest {quest_num} Content Requirements:
{f"- Focus on: {spec['content_focus']}" if quest_num == 1 else f"- Focus exclusively on: {spec['content_focus']} (building on foundational knowledge from Quest 1)" if quest_num == 2 else f"- Focus exclusively on: {spec['content_focus']} (assuming knowledge from Quests 1-2)" if quest_num == 3 else f"- Focus exclusively on: {spec['content_focus']} (building on Quests 1-3)" if quest_num == 4 else f"- Focus exclusively on: {spec['content_focus']} (synthesizing all previous quest knowledge)"}
- Write 250-300 words of specialized content ONLY about this quest's focus area
- Use distinct headings that reflect THIS quest's unique content area
- No generic "introduction" or "key concepts" - use specific headings for this quest's topic
- Include detailed examples specific to this quest's focus area

IMPORTANT: You must respond with ONLY valid JSON. No markdown formatting, no explanations, just pure JSON.

Generate this exact JSON structure with content focused ONLY on {spec['content_focus']}:
{{
    "title": "Quest {quest_num}: {spec['title']}",
    "content": "Write 250-300 words focused exclusively on {spec['content_focus']} for {topic}. Use specific HTML headings that reflect THIS quest's focus area - NO generic headings like 'Introduction' or 'Key Concepts'. Structure as distinct sections with detailed explanations, specific examples, and technical details relevant to this quest's specialized focus area. Use proper HTML tags: <h4>Specific Section Title</h4><p>Detailed content</p><ul><li>Specific points</li></ul>",
    "key_points": ["Specific learning point about {spec['content_focus']}", "Detailed insight about this quest's focus area", "Technical aspect of this quest's topic", "Important detail specific to this quest's content", "Advanced point about this quest's specialized area"],
    "fun_facts": ["Surprising fact specifically about {spec['content_focus']} in {topic}", "Fascinating detail about this quest's focus area", "Unexpected insight about this quest's specialized topic"],
    "visual_suggestions": ["Specific diagram for this quest's content area", "Chart/illustration relevant to this quest's focus"],
    "resources": [
        {{"title": "Khan Academy - {topic}", "url": "https://www.khanacademy.org/search?search_again=1&search_query={topic.replace(' ', '+')}", "description": "Interactive lessons and practice exercises"}},
        {{"title": "Wikipedia - {topic}", "url": "https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}", "description": "Comprehensive reference and additional details"}}
    ]"""

        if spec["has_quiz"]:
            if spec["quiz_type"] == "true_false":
                system_prompt += f""",
    "quiz": {{
        "type": "true_false",
        "instructions": "Select True or False for each statement about {spec['content_focus']} in {topic}",
        "questions": [
            {{"id": "q1", "question": "Create a specific true/false statement testing THIS quest's content focus: {spec['content_focus']}", "type": "true_false"}},
            {{"id": "q2", "question": "Create another true/false statement about {spec['content_focus']} that requires understanding, not just recall", "type": "true_false"}},
            {{"id": "q3", "question": "Create a true/false statement that tests application of knowledge about {spec['content_focus']}", "type": "true_false"}},
            {{"id": "q4", "question": "Create a challenging true/false statement about {spec['content_focus']} that requires analysis", "type": "true_false"}},
            {{"id": "q5", "question": "Create a true/false statement about implications or consequences of {spec['content_focus']}", "type": "true_false"}}
        ],
        "correct_answers": {{"q1": "true", "q2": "false", "q3": "true", "q4": "false", "q5": "true"}}
    }}"""
            elif spec["quiz_type"] == "matching":
                system_prompt += f""",
    "quiz": {{
        "type": "matching",
        "instructions": "Match each term on the left with its correct definition on the right",
        "left_items": ["Important term 1", "Important term 2", "Important term 3", "Important term 4", "Important term 5"],
        "right_items": ["Definition for term 1", "Definition for term 2", "Definition for term 3", "Definition for term 4", "Definition for term 5"],
        "correct_matches": {{"Important term 1": "Definition for term 1", "Important term 2": "Definition for term 2", "Important term 3": "Definition for term 3", "Important term 4": "Definition for term 4", "Important term 5": "Definition for term 5"}}
    }}"""
            elif spec["quiz_type"] == "multiple_choice":
                system_prompt += f""",
    "quiz": {{
        "type": "multiple_choice", 
        "instructions": "Select the best answer for each question about {spec['content_focus']} in {topic}",
        "questions": [
            {{"id": "q1", "question": "Create specific question testing understanding of {spec['content_focus']} - require application, not just recall", "options": ["Correct answer based on content", "Plausible but incorrect distractor", "Another plausible distractor", "Third plausible distractor"], "type": "multiple_choice"}},
            {{"id": "q2", "question": "Create analytical question about {spec['content_focus']} that tests deeper understanding", "options": ["Correct analytical answer", "Incorrect but reasonable option", "Another incorrect option", "Third incorrect option"], "type": "multiple_choice"}},
            {{"id": "q3", "question": "Create problem-solving question related to {spec['content_focus']} requiring application", "options": ["Correct solution", "Common misconception", "Partially correct but incomplete", "Incorrect approach"], "type": "multiple_choice"}},
            {{"id": "q4", "question": "Create comparison/evaluation question about {spec['content_focus']}", "options": ["Best evaluation/comparison", "Incorrect evaluation", "Another incorrect option", "Third incorrect option"], "type": "multiple_choice"}},
            {{"id": "q5", "question": "Create synthesis question about {spec['content_focus']} connecting to broader implications", "options": ["Correct synthesis", "Incorrect connection", "Another wrong connection", "Third wrong connection"], "type": "multiple_choice"}}
        ],
        "correct_answers": {{"q1": "Correct answer", "q2": "Correct answer", "q3": "Correct answer", "q4": "Correct answer", "q5": "Correct answer"}}
    }}"""
            elif spec["quiz_type"] == "mixed":
                system_prompt += f""",
    "quiz": {{
        "type": "mixed",
        "instructions": "Answer all questions about {topic} - mix of True/False, Matching, and Multiple Choice",
        "questions": [
            {{"id": "q1", "question": "Create specific true/false statement about key concept", "type": "true_false"}},
            {{"id": "q2", "question": "Create specific true/false statement about process/mechanism", "type": "true_false"}},
            {{"id": "q3", "question": "Create specific true/false statement about application", "type": "true_false"}},
            {{"id": "q4", "question": "Important term from content", "options": ["Correct definition", "Distractor 1", "Distractor 2"], "type": "matching"}},
            {{"id": "q5", "question": "Another important term", "options": ["Correct definition", "Distractor 1", "Distractor 2"], "type": "matching"}},
            {{"id": "q6", "question": "Third important term", "options": ["Correct definition", "Distractor 1", "Distractor 2"], "type": "matching"}},
            {{"id": "q7", "question": "Create MCQ about main concept", "options": ["Correct answer", "Distractor 1", "Distractor 2", "Distractor 3"], "type": "multiple_choice"}},
            {{"id": "q8", "question": "Create MCQ about practical application", "options": ["Correct answer", "Distractor 1", "Distractor 2", "Distractor 3"], "type": "multiple_choice"}},
            {{"id": "q9", "question": "Create MCQ about significance/impact", "options": ["Correct answer", "Distractor 1", "Distractor 2", "Distractor 3"], "type": "multiple_choice"}},
            {{"id": "q10", "question": "Create comprehensive MCQ testing synthesis", "options": ["Correct answer", "Distractor 1", "Distractor 2", "Distractor 3"], "type": "multiple_choice"}}
        ],
        "correct_answers": {{"q1": "true", "q2": "false", "q3": "true", "q4": "Correct definition", "q5": "Correct definition", "q6": "Correct definition", "q7": "Correct answer", "q8": "Correct answer", "q9": "Correct answer", "q10": "Correct answer"}}
    }}"""

        system_prompt += "\n}\n\nEnsure all content is accurate, educational, and appropriate for the quest level. Make the content engaging and progressive. Replace all placeholder text with actual topic-specific content."

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
            
            # Try to parse JSON response with better error handling
            try:
                # Clean up the response - remove any markdown formatting
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                quest_data = json.loads(content)
                
                # Validate required fields
                required_fields = ['title', 'content', 'key_points', 'fun_facts', 'visual_suggestions', 'resources']
                if spec.get('has_quiz'):
                    required_fields.append('quiz')
                
                for field in required_fields:
                    if field not in quest_data:
                        logging.error(f"Missing required field '{field}' in quest response")
                        return create_fallback_quest_content(topic, quest_num, spec)
                
                # Enrich visual suggestions with actual images
                quest_data = enrich_visual_suggestions_with_images(quest_data, topic)
                
                return quest_data
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON from Groq response for quest {quest_num}: {str(e)}")
                logging.error(f"Raw response content: {content[:500]}...")
                return create_fallback_quest_content(topic, quest_num, spec)
        else:
            logging.error(f"Groq API error: {response.status_code} - {response.text}")
            return create_fallback_quest_content(topic, quest_num, spec)
            
    except Exception as e:
        logging.error(f"Error generating quest content: {str(e)}")
        # Use quest specs for fallback
        quest_specs = {
            1: {"title": "Foundations & Core Principles", "has_quiz": False},
            2: {"title": "Mechanisms & Processes", "has_quiz": True, "quiz_type": "true_false"},
            3: {"title": "Advanced Systems & Interactions", "has_quiz": True, "quiz_type": "matching"},
            4: {"title": "Real-World Applications & Impact", "has_quiz": True, "quiz_type": "multiple_choice"},
            5: {"title": "Innovations & Future Directions", "has_quiz": True, "quiz_type": "mixed"}
        }
        fallback_spec = quest_specs.get(quest_num, {"title": "Learning Quest", "has_quiz": False})
        return create_fallback_quest_content(topic, quest_num, fallback_spec)

def create_fallback_quest_content(topic: str, quest_num: int, spec: Dict) -> Dict[str, Any]:
    """Create educational fallback content when AI API fails"""
    
    # Create topic-specific content based on quest level
    quest_descriptions = {
        1: f"Welcome to your learning journey about {topic}! This introductory quest will establish the foundational knowledge you need to understand this fascinating subject. We'll start with basic definitions, explore why this topic matters, and set the stage for deeper learning in subsequent quests.",
        2: f"Now that you have a foundation, let's dive deeper into the fundamental concepts of {topic}. This quest will expand your understanding by exploring key principles, examining how different components work together, and introducing important terminology that experts use in this field.",
        3: f"It's time to explore the more sophisticated aspects of {topic}. In this quest, we'll examine complex relationships, analyze interconnected systems, and understand how advanced concepts build upon the basics you've already learned.",
        4: f"Let's see {topic} in action! This practical quest focuses on real-world applications, case studies, and examples of how this knowledge is used to solve problems and create innovations in various industries and contexts.",
        5: f"Congratulations on reaching the final quest! Here we'll integrate everything you've learned about {topic}, explore cutting-edge developments, and help you master the complete picture of this subject. You'll leave with comprehensive understanding and practical knowledge."
    }
    
    content = {
        "title": f"Quest {quest_num}: {spec['title']}",
        "content": quest_descriptions.get(quest_num, f"Explore the fascinating world of {topic} in this comprehensive quest. {spec['description']}"),
        "key_points": [
            f"Core principles and definitions of {topic}",
            f"Historical development and significance of {topic}",
            f"Key components and how they interact",
            f"Real-world applications and examples",
            f"Current research and future directions"
        ],
        "fun_facts": [
            f"Research in {topic} has led to breakthrough discoveries that changed our understanding",
            f"The principles of {topic} are applied in surprising ways across different industries",
            f"Scientists continue to make exciting new discoveries in {topic} every year"
        ],
        "visual_suggestions": [
            {
                "description": f"Interactive diagram showing the key components of {topic}",
                "images": []
            },
            {
                "description": f"Timeline visualization of major developments in {topic}",
                "images": []
            }
        ],
        "resources": [
            {"title": f"Khan Academy - {topic}", "url": f"https://www.khanacademy.org/search?search_again=1&search_query={topic.replace(' ', '+')}", "description": "Interactive lessons and practice exercises"},
            {"title": f"Wikipedia - {topic}", "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}", "description": "Comprehensive reference and additional details"}
        ]
    }
    
    if spec.get("has_quiz"):
        content["quiz"] = create_fallback_quiz(topic, spec)
    
    # Enrich the fallback visual suggestions with images too
    content = enrich_visual_suggestions_with_images(content, topic)
    
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
    
    elif quiz_type == "matching":
        return {
            "type": "matching",
            "instructions": "Match each term on the left with its correct definition on the right",
            "left_items": [f"Basic {topic} concept 1", f"Key {topic} principle", f"Important {topic} method", f"{topic} application", f"Advanced {topic} idea"],
            "right_items": [f"Fundamental principle of {topic}", f"Primary method used in {topic}", f"Core concept in {topic} studies", f"Practical use of {topic}", f"Complex aspect of {topic}"],
            "correct_matches": {
                f"Basic {topic} concept 1": f"Core concept in {topic} studies",
                f"Key {topic} principle": f"Fundamental principle of {topic}",
                f"Important {topic} method": f"Primary method used in {topic}",
                f"{topic} application": f"Practical use of {topic}",
                f"Advanced {topic} idea": f"Complex aspect of {topic}"
            }
        }
    
    elif quiz_type == "multiple_choice":
        return {
            "type": "multiple_choice",
            "instructions": "Select the best answer for each question",
            "questions": [
                {"id": "q1", "question": f"What is the main focus of {topic}?", "options": [f"Understanding {topic} principles", "Random concepts", "Unrelated topics", "None of the above"], "type": "multiple_choice"},
                {"id": "q2", "question": f"Which is most important in {topic}?", "options": ["Basic knowledge", "Advanced applications", f"Core {topic} concepts", "External factors"], "type": "multiple_choice"}
            ],
            "correct_answers": {"q1": f"Understanding {topic} principles", "q2": f"Core {topic} concepts"}
        }
    
    # Default fallback
    return {
        "type": quiz_type,
        "instructions": "Complete the quiz questions",
        "questions": [],
        "correct_answers": {}
    }
